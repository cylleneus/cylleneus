import unicodedata
import re
from indic_transliteration import sanscript

DEVANAGARI = sanscript.DEVANAGARI
SLP1 = sanscript.SLP1

iast_mapping = {
    "C": "ch",
    "G": "gh",
    "J": "jh",
    "K": "kh",
    "W": "ṭh",
    "P": "ph",
    "Q": "ḍh",
    "D": "dh",
    "B": "bh",
    "T": "th",
    "O": "au",
    "E": "ai",
    "H": "ḥ",
    "A": "ā",
    "I": "ī",
    "U": "ū",
    "f": "ṛ",
    "F": "ṝ",
    "L": "ḷ",
    "M": "ṃ",
    "q": "ḍ",
    "N": "ṅ",
    "R": "ṇ",
    "S": "ś",
    "Y": "ñ",
    "x": "l̥",
    "X": "l̥̄",
    "w": "ṭ",
    "z": "ṣ",
}


def slp2deva(s):
    return unicodedata.normalize(
        "NFC", sanscript.transliterate(s, SLP1, DEVANAGARI)
    )


def iast2slp(s):
    for k, v in iast_mapping.items():
        s = re.sub(v, k, s)
    return s
