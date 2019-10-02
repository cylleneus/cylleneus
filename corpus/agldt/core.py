import codecs
import string
from pathlib import Path

import lxml.etree as et
import settings
from utils import nrange


# Glob pattern for indexing
glob = '*.tb.txt'

# Function to fetch text from corpus
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
    start = int(meta['start']['sent_id'])
    end = int(meta['end']['sent_id'])
    start_sentence = doc.find(f".//sentence[@id='{start}']")
    end_sentence = doc.find(f".//sentence[@id='{end}']")

    pre = []
    current_sentence = start_sentence.getprevious()
    i = 0
    while i < settings.LINES_OF_CONTEXT and current_sentence is not None:
        tokens = [
            token.get('form')
            for token in current_sentence.findall('word')
        ]
        text = ''.join([
            token + " "
            if i+1 < len(tokens) and tokens[i+1] not in string.punctuation
            else token
            for i, token in enumerate(tokens)
        ])
        pre.append(f"<pre>{text}</pre>")
        i += 1
        current_sentence = current_sentence.getprevious()

    hlites = set([hlite[-1] for hlite in meta['hlites']])

    match = []
    current_sentence = start_sentence
    limit_sentence = end_sentence.getnext()
    while current_sentence != limit_sentence and current_sentence is not None:
        tokens = [
            (token.get('id'), token.get('form'))
            for token in current_sentence.findall('word')]
        text = ''.join([
            (f"<em>{token}</em>"
            if id in hlites
            else
            f"{token}") + " "
            if i+1 < len(tokens) and tokens[i+1][1] not in string.punctuation
            else
            (f"<em>{token}</em>"
             if id in hlites
             else
             f"{token}")
            for i, (id, token) in enumerate(tokens)
        ])
        match.append(f"<match>{text}</match>")
        current_sentence = current_sentence.getnext()

    post = []
    current_sentence = end_sentence.getnext()
    i = 0
    while i < settings.LINES_OF_CONTEXT and current_sentence is not None:
        tokens = [
            token.get('form')
            for token in current_sentence.findall('word')
        ]
        text = ''.join([
            token + " "
            if i + 1 < len(tokens) and tokens[i + 1] not in string.punctuation
            else token
            for i, token in enumerate(tokens)
        ])
        post.append(f"<post>{text}</post>")
        i += 1
        current_sentence = current_sentence.getnext()

    if 'poem' in divs or (len(divs) == 2 and divs[-1] in ['line', 'verse']):
        joiner = '\n\n'
    else:
        joiner = ' '
    parts = pre + match + post
    text = f'{joiner}'.join(parts)

    return urn, reference, text


# TODO: how to handle future periphrastics?
def merge_compound(part: str, aux: str, morpho: str=None):
    pos: str = 'v'
    person = aux[1]
    number = part[2]
    if part[3] == 'f':
        tense = aux[3]
    elif part[3] == 'r':
        if aux[3] in 'pr':
            tense = 'r'
        elif aux[3] in 'iu':
            tense = 'u'
        elif aux[3] == 'f':
            tense = 't'
    mood = aux[4]
    voice = part[5]
    gender = part[6]
    case = '-'
    group = morpho[8] if morpho else '-'
    stem = morpho[9] if morpho else '-'
    return f"{pos}{person}{number}{tense}{mood}{voice}{gender}{case}{group}{stem}"


pos_convert = {
    'n': 'n',
    'v': 'v',
    'a': 'a',
    'r': 'p',  # preposition
    'd': 'r',  # adverb
    'p': 'o',  # pronoun
    'u': '-',
    'c': '-',
    'g': '-',
    '-': '-',
    'l': '-',  # article
    'x': '-',  # interrogative
    'i': '-',  # interjection
    'e': '-',  # exclamation
    'm': 'a'  # numeral: or 'n'? ['ATR']
}


def agldt2wn(agldt, morpho=None):  # optionally pass in a lemma's info for enrichment
    pos = pos_convert[agldt[0]]
    if pos == 'v':
        person = agldt[1]
    elif pos in 'ar':
        # degree
        person = agldt[8] if agldt[8] not in '-_' else 'p'
    elif pos == 'o' and morpho and morpho[0] == 'a':
        pos = morpho[0]
        person = morpho[1]
    else:
        person = '-'
    number = agldt[2]
    tense = agldt[3]
    mood = agldt[4]  # FIXME: gerund, gerundive, supine?
    voice = agldt[5]
    gender = agldt[6]
    case = agldt[7]
    group = morpho[8] if morpho and pos in 'nva' else '-'
    stem = morpho[9] if morpho and pos in 'nva' else '-'
    return f"{pos}{person}{number}{tense}{mood}{voice}{gender}{case}{group}{stem}"

relations = {
    "predicate": 'PRED',
    "hortatory subjunctive predicate": "PRED-HORT",
    "deliberative subjunctive predicate": "PRED-DELIB",
    "potential subjunctive predicate": "PRED-POTENT",
    "optative subjunctive predicate": "PRED-OPT",
    "interjection": "INTRJ",
    "parenthesis": "PARENTH",
    "subordinating conjunction": "AuxC",
    "preposition": "AuxP",
    "auxiliary verb": "AuxV",
    "attribute": "ATR",
    "adverb": "ADV",
    "coordinating conjunction": "COORD",
    "apposition": "APOS",
    "subject nominative": "N-SUBJ",
    "predicate nominative": "N-PRED",
    "genitive of possession": "G-POSS",
    "partitive genitive": "G-PART",
"objective genitive": "G-OBJEC",
"genitive of description": "G-DESC",
"genitive of characteristic": "G-CHAR",
"genitive of value": "G-VALUE",
"genitive of material": "G-MATER",
"genitive of the charge": "G-CHARGE",
"indirect object": "D-IO",
"dative of interest": "D-INTER",
"dative of possession": "D-POSS",
"dative of reference": "D-REFER",
"dative of agent": "D-AGENT",
"dative of purpose": "D-PURP",
"direct object": "A-DO",
"interior object": "A-INTOBJ",
"predicate accusative": "A-PRED",
"accusative subject": "A-SUBJ",
"accusative of orientation": "A-ORIENT",
"accusative of extent": "A-EXTENT",
"accusative of respect": "A-RESPECT",
"adverbial accusative": "A-ADVERB",
"accusative of exclamation": "A-EXCLAM",
"ablative of orientation": "AB-ORIENT",
"ablative of separation": "AB-SEPAR",
"ablative of cause": "AB-CAUSE",
"ablative of agent": "AB-AGENT",
"ablative absolute": "AB-ABSOL",
"ablative of comparison": "AB-COMPAR",
"ablative of location": "AB-LOCAT",
"ablative of respect": "AB-RESPECT",
"ablative of accompaniment": "AB-ACCOMP",
"ablative of description": "AB-DESCRIP",
"ablative of means": "AB-MEANS",
"ablative of manner": "AB-MANN",
"ablative of price": "AB-PRICE",
"ablative of degree of difference": "AB-DEGDIF",
"vocative": "V-VOC",
"locative": "L-LOCAT",
"relative clause": "ADJ-RC",
"relative clause of characteristic": "ADJ-RCCHAR",
"relative clause in indirect statement": "ADJ-RCINDSTAT",
"purpose clause": "ADV-PURP",
"result clause": "ADV-RESULT",
"consecutive clause": "ADV-CONSEC",
"conditional protasis": "ADV-PROTAS",
"temporal clause": "ADV-TEMPOR",
"circumstantial clause": "ADV-CIRCUMS",
"causal clause": "ADV-CAUSAL",
"concessive clause": "ADV-CONCESS",
"clause of comparison": "ADV-COMPAR",
"proviso clause": "ADV-PROVISO",
"relative clause of purpose": "ADV-RCPURP",
"relative clause of result": "ADV-RCRESULT",
"conditional relative clause": "ADV-RCCONDIT",
"indirect command": "NOM-SUBST",
"fear clause": "NOM-FEARCL",
"indirect question": "NOM-INDQUES",
"indirect statement": "NOM-INDSTAT",
"direct statement": "NOM-DIRSTAT",
"direct statement hortatory subjunctive": "NOM-DS-HORT",
"direct statement deliberative subjunctive": "NOM-DS-DELIB",
"direct statement potential subjunctive": "NOM-DS-POTENT",
"direct statement optative subjunctive": "NOM-DS-OPT",
"complimentary infinitive": "INF-COMP",
"historical infinitive": "INF-HIST",
"explanatory infinitive": "INF-EXPL",
"infinitive of purpose": "INF-PURP",
"exclamatory infinitive": "INF-EXCLAM",
}
