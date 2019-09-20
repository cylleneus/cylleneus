import codecs
from pathlib import Path

import lxml.etree as et
import settings
from utils import nrange, stringify

glob = '*.xml'


def fetch(work, meta, fragment):
    with codecs.open(work.corpus.text_dir / Path(work.doc['filename']), 'rb') as fp:
        value = fp.read()
    parser = et.XMLParser(encoding='utf-8')
    doc = et.XML(value, parser=parser)

    # URN
    urn = work.doc.get('urn', None)

    divs = meta['meta'].split('-')

    # Reference and hlite values
    ref_start = ', '.join(
        [f"{item}: {meta['start'][item]}" for item in meta['start'] if item in divs]
    )
    ref_end = ', '.join(
        [f"{item}: {meta['end'][item]}" for item in meta['end'] if item in divs]
    )
    reference = '-'.join([ref_start, ref_end]) if ref_end != ref_start else ref_start

    # Collect text and context
    start = list(
        int(meta['start'][div])
        for div in divs
    )
    end = list(
        int(meta['end'][div])
        for div in divs
    )
    pre = []
    pre_start = start[:-1] + [start[-1] - settings.LINES_OF_CONTEXT,]
    pre_end = start[:-1] + [start[-1] - 1,]
    for ref in nrange(pre_start, pre_end):
        xp = "/tei:TEI/tei:text/tei:body/tei:div"
        for div in ref:
            xp += f"/tei:div[@n='{div}']"
        sentence = doc.xpath(xp, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
        if len(sentence) == 0:
            xp = "/tei:TEI/tei:text/tei:body/tei:div"
            for div in ref[:-1]:
                xp += f"/tei:div[@n='{div}']"
            xp += f"/tei:l[@n='{ref[-1]}']"
            sentence = doc.xpath(xp, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})

        if len(sentence) != 0:
            text = stringify(sentence[0])
            pre.append(f"<pre>{text}</pre>")

    hlites = set([tuple(hlite) for hlite in meta['hlites']])  # only need token ids?

    match = []
    for ref in nrange(start, end):
        xp = "/tei:TEI/tei:text/tei:body/tei:div"
        for div in ref:
            xp += f"/tei:div[@n='{div}']"
        sentence = doc.xpath(xp, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
        if len(sentence) == 0:
            xp = "/tei:TEI/tei:text/tei:body/tei:div"
            for div in ref[:-1]:
                xp += f"/tei:div[@n='{div}']"
            xp += f"/tei:l[@n='{ref[-1]}']"
            sentence = doc.xpath(xp, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})

        if len(sentence) != 0:
            text = ' '.join([
                f"<em>{token}</em>"
                if (tuple(reversed([str(r) for r in ref])) + (str(i),)) in hlites
                else
                f"{token}"
                for i, token in enumerate(stringify(sentence[0]).split())
            ])
            match.append(f"<match>{text}</match>")

    post = []
    post_start = end[:-1] + [end[-1] + 1]
    post_end = end[:-1] + [end[-1] + settings.LINES_OF_CONTEXT,]
    for ref in nrange(post_start, post_end):
        xp = "/tei:TEI/tei:text/tei:body/tei:div"
        for div in ref:
            xp += f"/tei:div[@n='{div}']"
        sentence = doc.xpath(xp, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
        if len(sentence) == 0:
            xp = "/tei:TEI/tei:text/tei:body/tei:div"
            for div in ref[:-1]:
                xp += f"/tei:div[@n='{div}']"
            xp += f"/tei:l[@n='{ref[-1]}']"
            sentence = doc.xpath(xp, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})

        if len(sentence) != 0:
            text = stringify(sentence[0])
            post.append(f"<post>{text}</post>")

    if 'poem' in divs or (len(divs) == 2 and divs[-1] in ['line', 'verse']):
        joiner = '\n\n'
    else:
        joiner = ' '
    parts = pre + match + post
    text = f'{joiner}'.join(parts)
    return urn, reference, text
