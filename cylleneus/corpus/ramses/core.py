import codecs
import string

import lxml.etree as et

from cylleneus import settings

# Glob pattern for indexing
glob = "*.xml"


# Function to fetch text from corpus
def fetch(work, meta, fragment):
    with codecs.open(work.corpus.text_dir / work.filename[0], "rb") as fp:
        value = fp.read()
    parser = et.XMLParser(encoding="utf-8")
    doc = et.XML(value, parser=parser)

    # URN
    urn = work.doc[0].get("urn", None)

    divs = meta["meta"].split("-")

    # Reference and hlite values
    ref_start = ", ".join(
        [f"{item}: {meta['start'][item]}" for item in meta["start"] if item in divs]
    )
    ref_end = ", ".join(
        [f"{item}: {meta['end'][item]}" for item in meta["end"] if item in divs]
    )
    reference = "-".join([ref_start, ref_end]) if ref_end != ref_start else ref_start

    # Collect text and context
    start = ",".join([meta['start'][item] for item in meta["start"] if item in divs])
    end = ",".join([meta['end'][item] for item in meta["end"] if item in divs])

    start_position = doc.xpath(f".//position[text()='{start}']")[0]
    end_position = doc.xpath(f".//position[text()='{end}']")[0]

    limit_position = None
    current_position = end_position.getnext()

    while current_position is not None:
        if current_position.tag == "position":
            limit_position = current_position
            break
        else:
            current_position = current_position.getnext()

    match = []
    current_ref = start_position.text.split(',')
    current_position = start_position.getnext()
    while current_position is not None and current_position != limit_position:
        if current_position.tag == "word":
            ref = list((current_position.get("id"), *current_ref))
            if ref in meta["hlites"]:
                match.append(f"<em>{current_position.get('freeText')}</em>")
            else:
                match.append(current_position.get('freeText'))
        elif current_position.tag == "position":
            match.append('\n')
            current_ref = current_position.text.split(',')
        current_position = current_position.getnext() if current_position is not None else None

    joiner = " "
    parts = match
    text = f"{joiner}".join(parts)

    return urn, reference, f"<match>{text}</match>"
