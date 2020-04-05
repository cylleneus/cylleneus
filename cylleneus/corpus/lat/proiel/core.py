import codecs

import lxml.etree as et

from cylleneus import settings

# Language
language = "lat"

# Glob pattern for indexing
glob = "*.xml"

# Repo
repo = {
    'origin':   'https://github.com/cylleneus/proiel.git',
    'location': 'remote'
}


# Fetch text
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
    start = int(meta["start"]["sent_id"])
    end = int(meta["end"]["sent_id"])

    start_sentence = doc.find(f".//sentence[@id='{start}']")
    end_sentence = doc.find(f".//sentence[@id='{end}']")

    hlites = set([hlite[-1] for hlite in meta["hlites"]])  # only need token ids

    match = []
    current_sentence = start_sentence
    limit_sentence = end_sentence.getnext()
    while current_sentence != limit_sentence and current_sentence is not None:
        text = "".join(
            [
                f"<em>"
                f"{t.get('presentation-before') if t.get('presentation-before') else ''}"
                f"{t.get('form')}"
                f"{t.get('presentation-after') if t.get('presentation-after') else ''}"
                f"</em>"
                if t.get("id") in hlites
                else f"{t.get('presentation-before') if t.get('presentation-before') else ''}"
                     f"{t.get('form')}"
                     f"{t.get('presentation-after') if t.get('presentation-after') else ''}"
                for i, t in enumerate(current_sentence.findall("token"))
                if t.get("form")
            ]
        )
        match.append(f"<match>{text}</match>")
        current_sentence = current_sentence.getnext()

    pre = []
    current_sentence = start_sentence.getprevious()
    i = 0
    while i < settings.LINES_OF_CONTEXT and current_sentence is not None:
        text = "".join(
            [
                f"{token.get('presentation-before') if token.get('presentation-before') else ''}"
                f"{token.get('form')}"
                f"{token.get('presentation-after') if token.get('presentation-after') else ''}"
                for token in current_sentence.findall("token")
                if token.get("form")
            ]
        )
        pre.append(f"<pre>{text}</pre>")
        current_sentence = current_sentence.getprevious()
        i += 1

    post = []
    current_sentence = end_sentence.getnext()
    i = 0
    while i < settings.LINES_OF_CONTEXT and current_sentence is not None:
        text = "".join(
            [
                f"{token.get('presentation-before') if token.get('presentation-before') else ''}"
                f"{token.get('form')}"
                f"{token.get('presentation-after') if token.get('presentation-after') else ''}"
                for token in current_sentence.findall("token")
                if token.get("form")
            ]
        )
        pre.append(f"<post>{text}</post>")
        current_sentence = current_sentence.getnext()
        i += 1

    if "poem" in divs or (len(divs) == 2 and divs[-1] in ["line", "verse"]):
        joiner = "\n\n"
    else:
        joiner = " "
    parts = pre + match + post
    text = f"{joiner}".join(parts)
    return urn, reference, text


AUTHOR_TAB = {
    "Cicero": {
        "author": "M. Tullius Cicero",
        "code":   ["phi0474"],
        "works":  {
            "De officiis": {
                "title": "De Officiis",
                "code":  "phi055",
                "meta":  "book-section",
                "urn":   "urn:cts:latinLit:phi0474.phi055.perseus-lat1",
            },
        },
    },
}


def proiel2wn(pos: str, morpho: str):
    # 10-place morpho tag, basically Perseus, with final 'inflected' value
    pos_ = POS_TAG[pos]
    desc = ""
    for i, tag in enumerate(morpho):
        if i < 7:
            if tag != "-":
                desc += MORPHO[i][tag]
            else:
                desc += tag
        if i == 7:
            if tag != "-":
                desc = MORPHO[i][tag] + desc[1:]

    return f"{pos_}{desc}--"


POS_TAG = {
    "A-": "a",
    "Df": "r",
    "S-": "-",
    "Ma": "n",
    "Nb": "n",
    "C-": "-",
    "Pd": "o",
    "F-": "-",
    "Px": "o",
    "N-": "-",
    "I-": "-",
    "Du": "r",
    "Pi": "o",
    "Mo": "a",
    "Pp": "o",
    "Pk": "o",
    "Ps": "o",
    "Pt": "o",
    "R-": "p",
    "Ne": "n",
    "Py": "-",
    "Pc": "o",
    "Dq": "r",
    "Pr": "o",
    "G-": "-",
    "V-": "v",
    "X-": "-",
}
MORPHO = {
    0: {"1": "1", "2": "2", "3": "3", "x": "-"},
    1: {"s": "s", "d": "d", "p": "p", "x": "-"},
    2: {
        "p": "p",
        "i": "i",
        "r": "r",
        "s": "s",  # resultative
        "a": "a",  # aorist
        "u": "u",  # past
        "l": "l",
        "f": "f",
        "t": "t",
        "x": "-",
    },
    3: {
        "i": "i",
        "s": "s",
        "m": "m",
        "o": "o",  # optative
        "n": "n",
        "p": "p",
        "d": "g",  # gerund
        "g": "d",  # gerundive
        "u": "u",  # supine
        "x": "-",
        "y": "-",  # finiteness unspecified
        "e": "-",  # indicative or subjunctive
        "f": "-",  # indicative or imperative
        "h": "-",  # subjunctive or imperative
        "t": "-",  # finite
    },
    4: {"a": "a", "m": "m", "p": "p", "e": "-", "x": "-", },  # middle or passive
    5: {
        "m": "m",
        "f": "f",
        "n": "n",
        "p": "-",  # masculine or feminine
        "o": "-",  # masculine or neuter
        "r": "-",  # feminine or neuter
        "q": "a",  # masculine, feminine or neuter
        "x": "-",
    },
    6: {
        "n": "n",
        "a": "a",
        "o": "-",  # oblique
        "g": "g",
        "c": "-",  # genitive or dative
        "e": "-",  # accusative or dative
        "d": "d",
        "b": "a",
        "i": "-",  # instrumental
        "l": "l",
        "v": "v",
        "x": "-",  # uncertain
        "z": "-",  # unspecified
    },
    7: {"p": "p", "c": "c", "s": "s", "x": "-", "z": "-", },  # uncertain  # none
    8: {  # NOT USED (strength)
        "w": "w",  # weak
        "s": "s",  # strong
        "t": "t",  # weak or strong
    },
    9: {"n": "n", "i": "i", },  # NOT USED (inflection)  # non-inflecting  # inflecting
}

relations = {
    "adnominal":                 "adnom",
    "adverbial":                 "adv",
    "agens":                     "ag",
    "apposition":                "apos",
    "argument":                  "arg",
    "attribute":                 "atr",
    "auxiliary":                 "aux",
    "complement":                "comp",
    "expletive":                 "expl",
    "adnominal argument":        "narg",
    "non-subject":               "nonsub",
    "object":                    "obj",
    "oblique":                   "obl",
    "parenthetical predication": "parpred",
    "partitive":                 "part",
    "per":                       "peripheral",
    "predicate identity":        "pid",
    "predicate":                 "pred",
    "apposition or attribute":   "rel",
    "subject":                   "sub",
    "vocative":                  "voc",
    "open adverbial complement": "xadv",
    "open objective complement": "xobj",
    "external subject":          "xsub",
}
