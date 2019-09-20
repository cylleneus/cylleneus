from nltk.tokenize.punkt import PunktLanguageVars, PunktParameters, PunktSentenceTokenizer
import string

from .latin_exceptions import latin_exceptions


jvmap = str.maketrans('jv', 'iu', '')
punctuation = str.maketrans("", "", string.punctuation)

def roman_to_arabic(n: str):
    """ Convert a Roman numeral to an Arabic integer. """

    if isinstance(n, str):
        n = n.upper()
        numerals = {'M': 1000,
                    'D': 500,
                    'C': 100,
                    'L': 50,
                    'X': 10,
                    'V': 5,
                    'I': 1
                    }
        sum = 0
        for i in range(len(n)):
            try:
                value = numerals[n[i]]
                if i+1 < len(n) and numerals[n[i+1]] > value:
                    sum -= value
                else:
                    sum += value
            except KeyError:
                return None
        return sum

replacements = {
    'mecum': ['cum', 'me'],
    'tecum': ['cum', 'te'],
    'secum': ['cum', 'se'],
    'nobiscum': ['cum', 'nobis'],
    'vobiscum': ['cum', 'vobis'],
    'quocum': ['cum', 'quo'],
    'quacum': ['cum', 'qua'],
    'quicum': ['cum', 'qui'],
    'quibuscum': ['cum', 'quibus'],
    'sodes': ['si', 'audes'],
    'satin': ['satis', '-ne'],
    'scin': ['scis', '-ne'],
    'sultis': ['si', 'vultis'],
    'similist': ['similis', 'est'],
    'qualist': ['qualis', 'est'],
    'C.': ['Gaius'],
    'L.': ['Lucius'],
    'M.': ['Marcus'],
    'A.': ['Aulus'],
    'Cn.': ['Gnaeus'],
    'Sp.': ['Spurius'],
    "M'.": ['Manius'],
    'Ap.': ['Appius'],
    'Agr.': ['Agrippa'],
    'K.': ['Caeso'],
    'D.': ['Decimus'],
    'F.': ['Faustus'],
    'Mam.': ['Mamercus'],
    'N.': ['Numerius'],
    'Oct.': ['Octavius'],
    'Opet.': ['Opiter'],
    'Paul.': ['Paullus'],
    'Post.': ['Postumus'],
    'Pro.': ['Proculus'],
    'P.': ['Publius'],
    'Q.': ['Quintus'],
    'Sert.': ['Sertor'],
    'Ser.': ['Servius'],
    'Sex.': ['Sextus'],
    'S.': ['Spurius'],
    'St.': ['Statius'],
    'Ti.': ['Tiberius'],
    'T.': ['Titus'],
    'V.': ['Vibius'],
    'Vol.': ['Volesus'],
    'Vop.': ['Vopiscus'],
    'a.d.': ['ante', 'diem'],
    'a.': ['ante'],
    'd.': ['diem'],
    'Kal.': ['Kalendas'],
    'Id.': ['Idus'],
    'Non.': ['Nonas'],
    'Kal': ['Kalendas'],
    'Kalend': ['Kalendas'],
    'Id': ['Idus'],
    'Non': ['Nonas'],
    'Ianuar': ['Ianuarias'],
    'Febr': ['Februarias'],
    'Septembr': ['Septembris'],
    'Octobr': ['Octobris'],
    'Novembr': ['Novembris'],
    'Decembr': ['Decembris'],
    'Quint.': ['Quintilis'],
    'Sextil.': ['Sextilis'],
    'pr': ['pridie'],
    'Pr.': ['pridie'],
    'HS': ['sestertios'],
}

editorial = {
    'ante quam': 'antequam',
    'post quam': 'postquam',
    'me hercule': 'mehercule',
    'quam ob rem': 'quamobrem',
    'nihilo setius': 'nihilosetius',
    'nihilo secius': 'nihilosecius',
}

punkt_param = PunktParameters()
abbreviations = ['c', 'l', 'm', 'p', 'q', 't', 'ti', 'sex', 'a', 'd', 'cn', 'sp', "m'", 'ser', 'ap', 'n',
                 'v', 'k', 'mam', 'post', 'f', 'oct', 'opet', 'paul', 'pro', 'sert', 'st', 'sta', 'v', 'vol', 'vop']
punkt_param.abbrev_types = set(abbreviations)
sent_tokenizer = PunktSentenceTokenizer(punkt_param)

# [] and <> can appear within words as editorial conventions
class PunktLatinVars(PunktLanguageVars):
    _re_non_word_chars = r"(?:[?!)\";}\*:@\'\({])"
    """Characters that cannot appear within words"""

    _word_tokenize_fmt = r'''(
        %(MultiChar)s
        |
        (?=%(WordStart)s)\S+?                   # Accept word characters until end is found
        (?=                                     # Sequences marking a word's end
            \s|                                 # White-space
            $|                                  # End-of-string
            %(NonWord)s|%(MultiChar)s|          # Punctuation
            ,(?=$|\s|%(NonWord)s|%(MultiChar)s) # Comma if at end of word
        )
        |
        \S                                      
    )'''
word_tokenizer = PunktLatinVars()

class PunktLatinCharsVars(PunktLanguageVars):
    _re_non_word_chars = r"(?:[\[\]<>?!)\";}\*:@\({])" # remove []<>? ' can appear in, e.g., adgressu's
    """Characters that cannot appear within words"""

    _word_tokenize_fmt = r'''(
        %(MultiChar)s
        |
        (?=%(WordStart)s)\S+?                   # Accept word characters until end is found
        (?=                                     # Sequences marking a word's end
            \s|                                 # White-space
            $|                                  # End-of-string
            %(NonWord)s|%(MultiChar)s|          # Punctuation
            ,(?=$|\s|%(NonWord)s|%(MultiChar)s) # Comma if at end of word
        )
        |
        \s                                      # normally \S!
        |%(NonWord)s|%(MultiChar)s|,            # tokenize punctuation
    )'''

enclitics = ['que', 'ne', 'n', 'ue', 've', 'st', "'s"]
exceptions = list(set(enclitics + latin_exceptions + ['duplione', 'declinatione', 'altitudine', 'contentione', 'Ion']))

