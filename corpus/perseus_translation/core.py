import codecs
from itertools import chain
from pathlib import Path
import re

import lxml.etree as et
import settings
from utils import alnum, nrange, stringify

# Glob pattern for indexing
glob = '*-sentalign.txt'


# Fetch text
def fetch(work, meta, fragment):
    with codecs.open(work.corpus.text_dir / Path(work.doc['filename']), 'rb') as fp:
        value = fp.read()
    parser = et.XMLParser(encoding='utf-8')
    doc = et.XML(value, parser=parser)

    # URN
    urn = work.doc.get('urn', None)

    divs = meta['meta'].split('-')
    divs += ["align"]
    start_sent_id = meta['start']['sent_id']
    end_sent_id = meta['end']['sent_id']

    # Reference and hlite values
    ref_start = ', '.join(
        [f"{item}: {meta['start'][item]}" for item in meta['start'] if item in divs]
    )
    ref_end = ', '.join(
        [f"{item}: {meta['end'][item]}" for item in meta['end'] if item in divs]
    )
    reference = '-'.join([ref_start, ref_end]) if ref_end != ref_start else ref_start

    # Collect text and context
    start = {
        div: alnum(meta['start'][div])
        for div in divs
    }
    end = {
        div: alnum(meta['end'][div])
        for div in divs
    }
    refs = {
        refpattern.get('n'): re.sub(
            r"#xpath\((.*?)\)",
            r"\1",
            re.sub(r"\$\d+", "{}", refpattern.get('replacementPattern'))
        )
        for refpattern in reversed(doc.findall(
            ".//{http://www.tei-c.org/ns/1.0}cRefPattern"
        ))
    }

    start_sentence = doc.find(
        ".//{http://www.tei-c.org/ns/1.0}s[@{http://www.w3.org/XML/1998/namespace}id='" + start_sent_id + "']"
    )
    end_sentence = doc.find(
        ".//{http://www.tei-c.org/ns/1.0}s[@{http://www.w3.org/XML/1998/namespace}id='" + end_sent_id + "']"
    )

    # FIXME: highlighting
    hlites = []  # set([hlite[-1] for hlite in meta['hlites']])  # only need token ids?
    match = []
    current_sentence = start_sentence
    limit_sentence = end_sentence.getnext()
    while current_sentence != limit_sentence and current_sentence is not None:
        _text = stringify(current_sentence)
        if _text:
            text = ' '.join([
                f"<em>{token}</em>"
                if str(i) in hlites
                else
                f"{token}"
                for i, token in enumerate(_text.split())
            ])
            match.append(f"<match>{text}</match>")
        current_sentence = current_sentence.getnext()

    if 'poem' in divs or (len(divs) == 2 and divs[-1] in ['line', 'verse']) \
        or doc.find('.//{http://www.tei-c.org/ns/1.0}lb') is not None:
        joiner = '\n\n'
    else:
        joiner = ' '
    parts = match
    text = f'{joiner}'.join(parts)

    return urn, reference, text
