import codecs
import re
import string

import lxml.etree as et

from cylleneus import settings
from cylleneus.lang.lat import sent_tokenizer, word_tokenizer
from cylleneus.utils import nrange

# Description
description = "Digital Library of Late-Antique Latin Texts (DigilibLT)"

# Language
language = "lat"

# Glob pattern for indexing
glob = "*.xml"

# Repo
repo = {
    "origin":   "https://github.com/cylleneus/digiliblt.git",
    "raw":      "http://raw.github.com/cylleneus/digiliblt/master/",
    "location": "remote",
}


# Function to fetch text from corpus
def fetch(work, meta, fragment):
    with codecs.open(work.corpus.text_dir / work.filename[0], "rb") as fp:
        value = fp.read()
    parser = et.XMLParser(encoding="utf-8")
    doc = et.XML(value, parser=parser)

    # URN
    urn = (
        doc.find("{http://www.tei-c.org/ns/1.0}teiHeader")
            .find("{http://www.tei-c.org/ns/1.0}fileDesc")
            .find("{http://www.tei-c.org/ns/1.0}publicationStmt")
            .find("{http://www.tei-c.org/ns/1.0}idno")
            .text
    )

    tags = meta["meta"]
    if tags != "-":
        divs = tags.split("-")
    else:
        divs = []

    # Reference and hlite values
    ref_start = ", ".join(
        [f"{item}: {meta['start'][item]}" for item in meta["start"] if item in divs]
    )
    ref_end = ", ".join(
        [f"{item}: {meta['end'][item]}" for item in meta["end"] if item in divs]
    )
    reference = "-".join([ref_start, ref_end]) if ref_end != ref_start else ref_start

    if divs:
        hlites = [
            tuple(hlite[div] for div in ["sent_id", "sect_sent", "sent_pos"])
            for hlite in meta["hlites"]
        ]
    else:
        hlites = [
            tuple(hlite[div] for div in ["sent_id", "sect_sent", "sent_pos"])
            for hlite in meta["hlites"]
        ]

    # Collect text and context
    start = int(meta["start"]["sent_id"]), int(meta["start"]["sect_sent"])
    end = int(meta["end"]["sent_id"]), int(meta["end"]["sect_sent"])

    sentences_by_refs = {}
    sentences_by_id = {}

    sect_sent = 0
    sent_id = 0

    for el in (
        doc
            .find("{http://www.tei-c.org/ns/1.0}text")
            .find("{http://www.tei-c.org/ns/1.0}body")
            .findall(".//{http://www.tei-c.org/ns/1.0}*")
    ):
        if el.tag == "{http://www.tei-c.org/ns/1.0}milestone":
            sect_sent = 0
        elif el.tag == "{http://www.tei-c.org/ns/1.0}div" and el.get("n"):
            sect_sent = 0

        if not el.text:
            text = el.tail if el.tail else ""
        else:
            text = el.text + (el.tail if el.tail else "")
        subs = [
            (r"<supplied>(.*?)</supplied>", "\1"),
            (r'<quote type="\w+?">(.+?)</quote>', "\1"),
            (r'<hi rend="\w+?">(.+?)</hi>', "\1"),
            (r'<g ref="\w+?">(.+?)</g>', "\1"),
            (r'<foreign xml:lang="\w+?">(\w+?)</foreign>', "\1"),
            (r"<del>.+?</del>", ""),
        ]
        for old, new in subs:
            text = re.sub(old, new, text)

        if text:
            for sentence in sent_tokenizer.tokenize(text):
                sent_id += 1
                sect_sent += 1

                sentence = sentence.strip()
                replacements = [
                    (r"\n", ""),
                    (r"\s+", " ")
                ]
                for old, new in replacements:
                    sentence = re.sub(old, new, sentence)
                sentences_by_refs[(sent_id, sect_sent)] = sentence
                sentences_by_id[sent_id] = sentence

    pre = []
    if start[0] > settings.LINES_OF_CONTEXT:
        pre_sent = start[0] - settings.LINES_OF_CONTEXT
    else:
        pre_sent = 1
    while pre_sent < start[0]:
        sentence = sentences_by_id.get(pre_sent, None)

        if sentence:
            pre.append(f"<pre>{sentence}</pre>")
        pre_sent += 1

    match = []
    for ref in nrange(start, end):
        sentence = sentences_by_refs.get(ref, None)
        if sentence:
            tokens = word_tokenizer.word_tokenize(sentence)
            n = 0
            for i, token in enumerate(tokens):
                if token != " " and token not in string.punctuation:
                    if (str(ref[0]), str(ref[1]), str(n + 1)) in hlites:
                        tokens[i] = f"<em>{token}</em>"
                    n += 1
            text = "".join(tokens)
            match.append(f"<match>{text}</match>")

    post = []
    for i in range(end[0] + 1, end[0] + settings.LINES_OF_CONTEXT + 1):
        sentence = sentences_by_id.get(i, None)
        if sentence:
            post.append(f"<post>{sentence}</post>")

    if "poem" in divs or (len(divs) == 2 and divs[-1] in ["line", "verse"]):
        joiner = "\n\n"
    else:
        joiner = " "
    parts = pre + match + post
    text = f"{joiner}".join(parts)

    return urn, reference, text
