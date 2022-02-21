import codecs
from pathlib import Path

import lxml.etree as et
from cylleneus.settings import LINES_OF_CONTEXT
from cylleneus.lang.lat import word_tokenizer

# Description
description = (
    "Corpus Automatum Multiplex Electorum Neolatinitatis Auctorum (CAMENA)"
)

# Language
language = "lat"

# Glob pattern for indexing
glob = "*.xml"

# Repo
repo = {
    "origin":   "https://github.com/cylleneus/camena.git",
    "raw":      "http://raw.github.com/cylleneus/camena/master/",
    "location": "remote",
}


# Function to fetch text from corpus
def fetch(work, meta, fragment):
    _, file = work.filename[0]
    with codecs.open(
        work.corpus.text_dir / file, "rb"
    ) as fp:
        value = fp.read()
    parser_utf8 = et.XMLParser(encoding="utf-8")
    parser_iso8859 = et.XMLParser(encoding="iso-8859-1")
    try:
        doc = et.XML(value, parser=parser_utf8)
    except:
        doc = et.XML(value, parser=parser_iso8859)

    # URN
    _, urn = work.urn[0]

    divs = meta["meta"].split("-")

    # Reference and hlite values
    ref_start = ", ".join(
        [
            f"{item}: {meta['start'][item]}"
            for item in meta["start"]
            if item in divs
        ]
    )
    ref_end = ", ".join(
        [
            f"{item}: {meta['end'][item]}"
            for item in meta["end"]
            if item in divs
        ]
    )
    reference = (
        "-".join([ref_start, ref_end]) if ref_end != ref_start else ref_start
    )
    hlites = {(hlite["sent_id"], hlite["sent_pos"]) for hlite in meta["hlites"]}
    
    # Collect text and context
    sentences = []
    for el in doc.find("text").find("body").iter():
        if el.tag in ["head", "p", "l"]:
            if not el.text:
                text = "".join(
                    [
                        (subel.text or "") + (subel.tail or "")
                        for subel in el.iter()
                        if subel.tag != el.tag
                    ]
                )
            else:
                text = el.text
            sentences.append(text)

    start = int(meta["start"]["sent_id"]) - 1
    end = int(meta["end"]["sent_id"]) - 1
    
    pre = [
        f"<pre>{sentence}</pre>"
        for sentence in sentences[start - LINES_OF_CONTEXT: start]
    ]
    match = [
        f"<match>"
        f'''{"".join([f"{' ' if i == 0 else ''}<em>{token}</em>" if (str(j + start + 1), str(i)) in hlites else token for j, sentence in enumerate(sentences[start:end + 1]) for i, token in enumerate(word_tokenizer.word_tokenize(sentence))])}'''
        f"</match>",
    ]
    
    post = [
        f"<post>{sentence}</post>"
        for sentence in sentences[start + (end - start) + 1: start + LINES_OF_CONTEXT]
    ]

    if "poem" in divs or (len(divs) == 2 and divs[-1] in ["line", "verse"]):
        joiner = "\n\n"
    else:
        joiner = " "
    parts = pre + match + post
    text = f"{joiner}".join(parts)

    return urn, reference, text
