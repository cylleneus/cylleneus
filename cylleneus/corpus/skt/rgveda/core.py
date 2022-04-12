import codecs
import json
from pathlib import Path

dir = Path(__file__).parent

# Description
description = "Rgveda semantically annotated corpus"

# Language
language = "skt"

# Glob pattern for indexing
glob = "*.conllu"

# Repo
repo = {
    "origin":   None,  # "https://github.com/cylleneus/dcs.git",
    "raw":      None,  # "https://raw.github.com/cylleneus/dcs/master/",
    "location": "local",
}


# Fetch text
def fetch(work, meta, fragment):
    _, file = work.filename[0]
    path = work.corpus.text_dir / file

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

    # Collect text and context
    with codecs.open(path, "r", "utf8") as fp:
        lines = fp.readlines()

    hlites = [
        (f"ṚV_{hlite['book']}_{hlite['hymn']}_{hlite['verse']}_{hlite['pada']}", int(hlite['sent_pos']))
        for hlite in meta["hlites"]
    ]

    start = f"ṚV_{meta['start']['book']}_{meta['start']['hymn']}_{meta['start']['verse']}_{meta['start']['pada']}"
    end = f"ṚV_{meta['end']['book']}_{meta['end']['hymn']}_{meta['end']['verse']}_{meta['end']['pada']}"
    
    match = []
    process = False
    current_sent_id = previous_sent_id = None
    for line in lines:
        line = line.strip()
        if line:
            if line.startswith("#"):
                try:
                    label, value = line.split("=", maxsplit=1)
                except ValueError:
                    continue
                label = label.strip('#').strip()
                value = value.strip()
                if label == "sent_id":
                    previous_sent_id = current_sent_id
                    current_sent_id = value
                    
                    if current_sent_id == start:
                        process = True
                    elif previous_sent_id == end:
                        process = False
                elif label == "text":
                    if process is True:
                        match_text = " ".join(
                            [
                                f"<em>{word}</em>"
                                if (current_sent_id, i + 1) in hlites
                                else word
                                for i, word in enumerate(value.split())
                            ]
                        )
                        match.append(f"<match>{match_text}</match>")
    joiner = "\n"
    parts = match
    text = f"{joiner}".join(parts)

    return urn, reference, text


with codecs.open(dir / Path("dcs_lemma_id.json"), "r", "utf8") as fp:
    lemma_id = json.load(fp)

with codecs.open(dir / Path("dcs_lemma_morpho.json"), "r", "utf8") as fp:
    lemma_morpho = json.load(fp)

with codecs.open(dir / Path("dcs_lemma_synsets.json"), "r", "utf8") as fp:
    lemma_synsets = json.load(fp)

with codecs.open(dir / Path("dcs_wn_mappings.json"), "r", "utf8") as fp:
    wn_mappings = json.load(fp)

xpos_mapping = {
    "CAD":  ("adverb", "ADV"),
    "CADA": ("preverbs (abhi)", "ADP"),
    "CADP": ("preverbs (pra)", "ADP"),
    "CCD":  ("coordinating conjunction", "CCONJ"),
    "CCM":  ("particles for comparison", "PART"),
    "CEM":  ("emphatic particle", "PART"),
    "CGDA": ("absolutive, gerund", "VERB/NOUN"),
    "CGDI": ("infinitive", "VERB/NOUN"),
    # "CIN":
    "CNG":  ("negation", "ADV/PART"),
    "CQT":  ("quotation particle", "PART"),
    "CSB":  ("subordinating conjunction", "SCONJ"),
    "CX":   ("other adverbs", "ADV/PART"),
    "JJ":   ("adjective", "ADJ"),
    "JQ":   ("quantifying adjective", "ADJ/DET"),
    "KDG2": ("gerundive", "VERB/ADJ"),
    "KDP":  ("participle", "VERB/ADJ"),
    "NC":   ("common noun", "NOUN"),
    # "NP": ("proper noun, ""),
    "NUM":  ("number", "NUM"),
    "PPP":  ("past participle", "VERB/ADJ"),
    "PPR":  ("personal pronoun", "PRON"),
    "PPX":  ("other pronouns", "PRON"),
    "PRC":  ("reciprocal pronoun", "PRON"),
    "PRD":  ("demonstrative pronoun", "PRON/DET"),
    # "PRF":
    "PRI":  ("indefinite pronoun", "PRON"),
    "PRL":  ("relative pronoun", "PRON/DET"),
    "PRQ":  ("interrogative pronoun", "PRON/DET"),
    "V":    ("finite verbal form", "VERB"),
}

pos_mapping = {
    "adverb":                    "CAD",
    "preverbs (abhi)":           "CADA",
    "preverbs (pra)":            "CADP",
    "coordinating conjunction":  "CCD",
    "particles for comparison":  "CCM",
    "emphatic particle":         "CEM",
    "absolutive, gerund":        "CGDA",
    "infinitive":                "CGDI",
    "negation":                  "CNG",
    "quotation particle":        "CQT",
    "subordinating conjunction": "CSB",
    "other adverbs":             "CX",
    "adjective":                 "JJ",
    "quantifying adjective":     "JQ",
    "gerundive":                 "KDG2",
    "participle":                "KDP",
    "common noun":               "NC",
    "number":                    "NUM",
    "past participle":           "PPP",
    "personal pronoun":          "PPR",
    "other pronouns":            "PPX",
    "reciprocal pronoun":        "PRC",
    "demonstrative pronoun":     "PRD",
    "indefinite pronoun":        "PRI",
    "relative pronoun":          "PRL",
    "interrogative pronoun":     "PRQ",
    "finite verbal form":        "V",
}


def parse_morpho(upos, morpho: str):
    parses = morpho.lower().split("|")
    inflections = {
        "pos":      upos,
        "person":   "-",
        "number":   "-",
        "tense":    "-",
        "mood":     "-",
        "voice":    "-",
        "gender":   "-",
        "case":     "-",
        "group":    "-",
        "stem":     "-",
        "verbform": "-",
    }
    inflections.update({tuple(parse.split("=")) for parse in parses})

    for k, v in inflections.items():
        if k not in ["group", "stem", "formation"]:
            inflections[k] = morpho_mappings[k].get(v, "-")
    if inflections["verbform"] != "-" and inflections["mood"] == "-":
        inflections["mood"] = inflections["verbform"]
    return "".join(
        [
            v
            for k, v in inflections.items()
            if k != "verbform" and k != "formation"
        ]
    )


morpho_mappings = {
    "pos":      {
        "CAD":  "r",
        "CCM":  "r",
        "CEM":  "r",
        "CGDA": "v",
        "CGDI": "v",
        "CQT":  "r",
        "CX":   "r",
        "JJ":   "a",
        "JQ":   "a",
        "KDG2": "v",
        "KDP":  "v",
        "NC":   "n",
        "NP":   "n",
        "NUM":  "n",
        "PPP":  "v",
        "V":    "v",
    },
    "person":   {
        # PERSON
        "1": "1",
        "2": "2",
        "3": "3",
    },
    "number":   {"1": "s", "2": "d", "3": "p", "sing": "s", "plur": "p"},
    "tense":    {"pres": "p", "perf": "r", "aor": "a", "fut": "f", "impf": "i"},
    "mood":     {
        "ind":  "i",
        "imp":  "m",
        "opt":  "o",
        "sub":  "s",
        "prec": "r",
        "cond": "c",
        "inj":  "j",
    },
    "voice":    {"act": "a", "mid": "m", "pass": "p", },
    "verbform": {"abs": "a", "ppp": "p", "ger": "g", "part": "p", "inf": "n"},
    "case":     {
        "nom": "n",
        "cpd": "c",
        "gen": "g",
        "dat": "d",
        "acc": "a",
        "abl": "b",
        "loc": "l",
        "ins": "i",
    },
    "gender":   {"masc": "m", "neut": "n", "fem": "f"},
}
