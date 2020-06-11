import codecs
import re
from itertools import product
from cylleneus.lang.grk.beta2unicode import beta2unicode
import lxml.etree as et

from cylleneus import settings

# Description
description = "Diorisis Ancient Greek Corpus (XML)"

# Language
language = "grk"

# Glob pattern for indexing
glob = "*.xml"

# Repo
repo = {
    "origin":   "https://github.com/cylleneus/diorisis.git",
    "raw":      "http://raw.github.com/cylleneus/diorisis/master/",
    "location": "remote",
}


# Fetch text
def fetch(work, meta, fragment):
    _, file = work.filename[0]

    with codecs.open(work.corpus.text_dir / file, "rb") as f:
        value = f.read()
    parser = et.XMLParser(encoding="utf-8")
    doc = et.XML(value, parser=parser)

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

    hlites = sorted(
        {(hlite["sent_id"], hlite["sent_pos"]) for hlite in meta["hlites"]}
    )

    # Collect text and context
    start = int(meta["start"]["sent_id"])
    end = int(meta["end"]["sent_id"])

    pre_sentences = []
    for pre_id in range(start - settings.LINES_OF_CONTEXT, start):
        pre_sentence = (
            doc.find(".//text").find("body").find(f"sentence[@id='{pre_id}']")
        )
        if pre_sentence is not None:
            text = " ".join(
                beta2unicode(el.get("form", "").upper())
                if el.tag == "word"
                else beta2unicode(el.get("mark", ""))
                for el in pre_sentence.iter()
                if el.tag in ["word", "punct"]
            )
            pre_sentences.append(f"<pre>{text}</pre>")

    post_sentences = []
    for post_id in range(end + 1, end + settings.LINES_OF_CONTEXT):
        post_sentence = (
            doc.find(".//text").find("body").find(f"sentence[@id='{post_id}']")
        )
        if post_sentence is not None:
            text = " ".join(
                beta2unicode(el.get("form", "").upper())
                if el.tag == "word"
                else beta2unicode(el.get("mark", ""))
                for el in post_sentence.iter()
                if el.tag in ["word", "punct"]
            )
            post_sentences.append(f"<pre>{text}</pre>")

    match_sentences = []
    for match_id in range(start, end + 1):
        match_sentence = (
            doc.find(".//text")
                .find("body")
                .find(f"sentence[@id='{match_id}']")
        )
        if match_sentence is not None:
            ref = match_sentence.get("location").split(".")
            text = " ".join(
                f"<em>{beta2unicode(el.get('form', '').upper())}</em>"
                if tuple([str(r) for r in ref] + [str(el.get("id")), ]) in hlites
                else beta2unicode(el.get("form", "").upper())
                if el.tag == "word"
                else beta2unicode(el.get("mark", ""))
                for el in match_sentence.iter()
                if el.tag in ["word", "punct"]
            )
            match_sentences.append(f"<match>{text}</match>")

    if "poem" in divs or (len(divs) == 2 and divs[-1] in ["line", "verse"]):
        joiner = "\n\n"
    else:
        joiner = " "
    parts = pre_sentences + match_sentences + post_sentences
    text = f"{joiner}".join(parts)
    urn = work.urn

    return urn, reference, text


pos_mapping = {
    "noun":         "n",  # pos
    "verb":         "v",
    "adjective":    "a",
    "adverb":       "r",
    "preposition":  "p",
    "pronoun":      "o",
    "proper":       "n",
    "particle":     "t",
    "conjunction":  "c",
    "article":      "e",
    "interjection": "i",
}

morpho_mapping = {
    "1st":           (1, "1"),  # person, degree
    "2nd":           (1, "2"),
    "3rd":           (1, "3"),
    "sg":            (2, "s"),  # number
    "du":            (2, "d"),
    "pl":            (2, "p"),
    "pres":          (3, "p"),  # tense
    "imperf":        (3, "i"),
    "fut":           (3, "f"),
    "aor":           (3, "a"),
    "perf":          (3, "r"),
    "plup":          (3, "l"),
    "futperf":       (3, "u"),
    "ind":           (4, "i"),  # mood
    "sub":           (4, "s"),
    "opt":           (4, "o"),
    "inf":           (4, "n"),
    "imp":           (4, "m"),
    "part":          (4, "p"),
    "act":           (5, "a"),  # voice
    "mid":           (5, "m"),
    "pass":          (5, "p"),
    "mp":            (5, "d"),
    "masc":          (6, "m"),  # gender
    "fem":           (6, "f"),
    "neut":          (6, "n"),
    "masc/fem":      (6, "c"),
    "masc/fem/neut": (6, "a"),
    "masc/neut":     (6, "C"),
    "nom":           (7, "n"),  # case
    "gen":           (7, "g"),
    "dat":           (7, "d"),
    "acc":           (7, "a"),
    "loc":           (7, "l"),
    "voc":           (7, "v"),
    "nom/voc/acc":   (7, "n"),
}


def diorisis2wn(POS: str, morpho: str) -> list:
    morpho = re.sub(r" \(.*?\)", "", morpho)
    pos = pos_mapping[POS]

    morphs = morpho.split()

    variations = {i: [] for i in range(10)}
    variations[0].append(pos)
    for morph in morphs:
        for variation in morph.split("/"):
            i, v = morpho_mapping.get(variation, (None, None))
            if i is not None and v is not None:
                variations[i].append(v)

    for k, v in variations.items():
        if len(v) == 0:
            variations[k].append("-")
    return ["".join(variation) for variation in product(*variations.values())]
