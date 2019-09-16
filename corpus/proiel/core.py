import codecs
import lxml.etree as et
import settings
from utils import nrange

def get(hit, meta, fragment):
    with codecs.open('corpus/proiel/text/' + hit['filename'], 'rb') as fp:
        value = fp.read()
    parser = et.XMLParser(encoding='utf-8')
    doc = et.XML(value, parser=parser)

    # URN
    urn = hit.get('urn', None)

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
    start = int(meta['start']['sent_id'])
    end = int(meta['end']['sent_id'])

    pre = []
    pre_start = start - settings.LINES_OF_CONTEXT
    for id in nrange(pre_start, start[0]):
        sentence = doc.find(f'.//sentence[@id={id}]')
        text = sentence.text
        pre.append(f"<pre>{text}</pre>")

    hlites = set([tuple(hlite) for hlite in meta['hlites']])

    match = []
    for id in nrange(start, end):
        sentence = doc.find(f'.//sentence[@id={id}]')
        text = [
            f"<em>{t}</em>"
            if (id, str(i + 1)) in hlites
            else t
            for i, t in enumerate(sentence.text.split())
        ]
        match.append(f"<match>{' '.join(text)}</match>")

    post = []
    post_end = end + settings.LINES_OF_CONTEXT
    for id in nrange(end + 1, post_end):
        sentence = doc.find(f'.//sentence[@id={id}]')
        text = sentence.text
        post.append(f"<post>{text}</post>")

    if 'poem' in divs or (len(divs) == 2 and divs[-1] in ['line', 'verse']):
        joiner = '\n\n'
    else:
        joiner = ' '
    parts = pre + match + post
    text = f'{joiner}'.join(parts)

    return urn, reference, text


AUTHOR_TAB = \
    {
        "Cicero":
        {
            "author": "M. Tullius Cicero",
            "code":   ["phi0474"],
            "works":
                {
                    "De officiis":
                        {
                            "title": "De Officiis",
                            "code":  "phi055",
                            "meta":  "book-section",
                            'urn': 'urn:cts:latinLit:phi0474.phi055.perseus-lat1'
                        },
                },
        },
    }

def parse_proiel(pos: str, morpho: str):
    # 10-place morpho tag, basically Perseus, with final 'inflected' value
    pos_ = POS_TAG[pos]
    desc = ''
    for i, tag in enumerate(morpho):
        if i < 7:
            if tag != '-':
                desc += (MORPHO[i][tag])
            else:
                desc += tag
        if i == 7:
            if tag != '-':
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
    0: {
        "1": "1",
        "2": "2",
        "3": "3",
        "x": "-"
    },
    1:
        {
            "s": "s",
            "d": "d",
            "p": "p",
            "x": "-"
        },
    2: {
        "p": "p",
        "i": "i",
        "r": "r",
        "s": "s",    # resultative
        "a": "a",    # aorist
        "u": "u",    # past
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
        "t": "-"   # finite
    },
    4: {
        "a": "a",
        "m": "m",
        "p": "p",
        "e": "-",  # middle or passive
        "x": "-",
    },
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
        "c": "-", # genitive or dative
        "e": "-", # accusative or dative
        "d": "d",
        "b": "a",
        "i": "-", # instrumental
        "l": "l",
        "v": "v",
        "x": "-",  # uncertain
        "z": "-",  # unspecified
    },
    7: {
        "p": "p",
        "c": "c",
        "s": "s",
        "x": "-",  # uncertain
        "z": "-",  # none
    },
    8:  # NOT USED (strength)
        {
        "w": "w",  # weak
        "s": "s",  # strong
        "t": "t",  # weak or strong
    },
    9:  # NOT USED (inflection)
        {
            "n": "n",  # non-inflecting
            "i": "i",  # inflecting
    },
}

relations = {
    "adnominal": "adnom",
      "adverbial": "adv",
      "agens": "ag",
      "apposition": "apos",
      "argument": "arg",
      "attribute": "atr",
      "auxiliary": "aux",
      "complement": "comp",
      "expletive": "expl",
      "adnominal argument": "narg",
      "non-subject": "nonsub",
      "object": "obj",
      "oblique": "obl",
      "parenthetical predication": "parpred",
      "partitive": "part",
      "per": "peripheral",
      "predicate identity": "pid",
      "predicate": "pred",
      "apposition or attribute": "rel",
      "subject": "sub",
      "vocative": "voc",
      "open adverbial complement": "xadv",
      "open objective complement": "xobj",
      "external subject": "xsub",
}
