import codecs
from pathlib import Path
import re

import lxml.etree as et
from cylleneus import settings
from cylleneus.utils import alnum, stringify

# Description
description = "Perseus Digital Library (XML)"

# Language
language = "lat"

# Glob pattern for indexing
glob = "*.xml"

# Repo
repo = {
    "origin":   "https://github.com/cylleneus/perseus_xml.git",
    "raw":      "http://raw.github.com/cylleneus/perseus_xml/master/",
    "location": "remote",
}


# Fetch text
def fetch(work, meta, fragment):
    _, file = work.filename[0]
    with codecs.open(work.corpus.text_dir / file, "rb") as fp:
        value = fp.read()
    parser = et.XMLParser(encoding="utf-8")
    doc = et.XML(value, parser=parser)

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

    hlites = set(
        hlite["sent_pos"] for hlite in meta["hlites"]
    )  # only need token ids?

    # Collect text and context
    start = {div: alnum(meta["start"][div]) for div in divs}
    end = {div: alnum(meta["end"][div]) for div in divs}
    refs = {
        refpattern.get("n"): re.sub(
            r"#xpath\((.*?)\)",
            r"\1",
            re.sub(r"\$\d+", "{}", refpattern.get("replacementPattern")),
        )
        for refpattern in reversed(
            doc.findall(".//{http://www.tei-c.org/ns/1.0}cRefPattern")
        )
    }

    start_sentence = doc.xpath(
        refs[divs[-1]].format(
            *list(reversed([start[div] for div in divs if div in refs]))
        ),
        namespaces={"tei": "http://www.tei-c.org/ns/1.0"},
    )[0]
    end_sentence = doc.xpath(
        refs[divs[-1]].format(
            *list(reversed([end[div] for div in divs if div in refs]))
        ),
        namespaces={"tei": "http://www.tei-c.org/ns/1.0"},
    )[0]

    match = []
    current_sentence = start_sentence
    limit_sentence = end_sentence.getnext()
    while current_sentence != limit_sentence and current_sentence is not None:
        _text = stringify(current_sentence) or current_sentence.text
        if _text:
            text = " ".join(
                [
                    f"<em>{token}</em>" if str(i) in hlites else f"{token}"
                    for i, token in enumerate(_text.split())
                ]
            )
            match.append(f"<match>{text}</match>")
        current_sentence = current_sentence.getnext()

    pre = []
    current_sentence = start_sentence.getprevious()
    i = 0
    while i < settings.LINES_OF_CONTEXT and current_sentence is not None:
        if current_sentence.tag not in (
            "{http://www.tei-c.org/ns/1.0}lb",
            "{http://www.tei-c.org/ns/1.0}speaker",
            "{http://www.tei-c.org/ns/1.0}note",
            "{http://www.tei-c.org/ns/1.0}pb",
        ):
            text = stringify(current_sentence) or current_sentence.text
            if text:
                pre.append(f"<pre>{text}</pre>")
                i += 1
        current_sentence = current_sentence.getprevious()

    post = []
    current_sentence = end_sentence.getnext()
    i = 0
    while i < settings.LINES_OF_CONTEXT and current_sentence is not None:
        if current_sentence.tag not in (
            "{http://www.tei-c.org/ns/1.0}lb",
            "{http://www.tei-c.org/ns/1.0}speaker",
        ):
            text = stringify(current_sentence) or current_sentence.text
            if text:
                post.append(f"<post>{text}</post>")
                i += 1
        current_sentence = current_sentence.getnext()

    if (
        "poem" in divs
        or (len(divs) == 2 and divs[-1] in ["line", "verse"])
        or doc.find(".//{http://www.tei-c.org/ns/1.0}lb") is not None
    ):
        joiner = "\n\n"
    else:
        joiner = " "
    parts = pre + match + post
    text = f"{joiner}".join(parts)

    return urn, reference, text
