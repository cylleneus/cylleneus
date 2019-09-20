import codecs
import copy
import string
from pathlib import Path

import settings
from corpus.preprocessing import BasePreprocessor
from engine.analysis.acore import CylleneusToken
from engine.analysis.filters import AnnotationFilter, CachedLemmaFilter, CachedSynsetFilter, SemfieldFilter
from engine.analysis.tokenizers import Tokenizer
from engine.fields import *
from engine.schemas import BaseSchema
from lang.latin import compound, enclitics, exceptions, jvmap, proper_names, replacements, sent_tokenizer, \
    word_tokenizer


glob = '.txt'


class Preprocessor(BasePreprocessor):
    def parse(self, file: Path):
        with codecs.open(file, 'r', 'utf8') as fp:
            doc = fp.read()

        # Do some tidying up
        subs = [
            (r"\.,", "."),
            (r"([\w])\.([\w])", r"\1. \2"),
            (r",([\w])", r", \1"),
            (r"(?<=\w)\.\.", r" . ."),
            (r"([.,;:])([.,;:])", r"\1 \2"),
            (r"[\t\r\n ]+", " "),
            (r'\.\"', r'\"\.'),
            (r' ,', ','),
            (r'\[ \d+ \] ', ''),
            (r' \[,', '[,'),
            (r'\]\.', '.]')
        ]
        for pattern, repl in subs:
            doc = re.sub(pattern, repl, doc)
        return {
            'content': doc,
            'form': doc,
            'lemma': doc,
            'synset': doc,
            'annotation': doc,
            'semfield': doc,
            'filename': file.name,
            'datetime': datetime.now()
        }


class CachedTokenizer(Tokenizer):
    def __init__(self, **kwargs):
        super(CachedTokenizer, self).__init__()
        self.__dict__.update(**kwargs)
        self._cache = None
        self._docix = 0

    @property
    def cache(self):
        return copy.deepcopy(self._cache)

    def __call__(self, value: str, positions=True, chars=True,
                 keeporiginal=True, removestops=True, tokenize=True,
                 start_pos=0, start_char=0, mode='', **kwargs):
        if self._cache and kwargs.get('docix', None) == self._docix:
            yield from self.cache
        else:
            t = CylleneusToken(positions, chars, removestops=removestops, mode=mode, **kwargs)

            if t.mode == 'query':
                t.original = t.text = value.translate(jvmap)
                yield t
            else:
                if not tokenize:
                    t.original = t.text = value
                    t.boost = 1.0
                    if positions:
                        t.pos = start_pos
                    if chars:
                        t.startchar = start_char
                        t.endchar = start_char + len(value)
                    yield t
                else:
                    self._cache = []
                    self._docix = kwargs.get('docix', 0)

                    sents = sent_tokenizer.tokenize(value)
                    stopchars = str.maketrans('', '', string.punctuation.replace('-', ''))

                    tokens = []
                    sent_id = 0
                    for i, sent in enumerate(sents):
                        sent_id += i
                        temp_tokens = word_tokenizer.word_tokenize(sent)

                        if temp_tokens:
                            if temp_tokens[0].replace('j', 'i').replace('v', 'u') not in proper_names.proper_names:
                                temp_tokens[0] = temp_tokens[0]

                            if temp_tokens[-1].endswith('.'):
                                final_word = temp_tokens[-1][:-1]
                                del temp_tokens[-1]
                                temp_tokens += [final_word, '.']

                            skipflag = False
                            for ix, token in enumerate(temp_tokens):
                                if not skipflag:
                                    ppp = compound.is_ppp(token)
                                    if ppp:
                                        copula = compound.is_copula(temp_tokens[ix+1])
                                        if copula and ppp[1] == copula[2]:
                                            tense, mood, number, i = copula
                                            token = f"{token} {compound.copula[tense][mood][number][i]}"
                                            tokens.append(token)
                                            skipflag = True
                                        else:
                                            tokens.append(token)
                                    else:
                                        tokens.append(token)
                                else:
                                    skipflag = False
                    for pos, token in enumerate(tokens):
                        sent_pos = pos

                        t.meta = {
                            'sent_id': sent_id,
                            'sent_pos': sent_pos
                        }
                        t.boost = 1.0
                        if keeporiginal:
                            t.original = token
                        t.stopped = False
                        if positions:
                            t.pos = start_pos + pos
                        original_length = len(token)

                        ltoken = token.lstrip(string.punctuation)
                        ldiff = original_length - len(ltoken)
                        if ldiff != 0:
                            token = ltoken
                        rtoken = token.rstrip(string.punctuation)
                        rdiff = len(token) - len(rtoken)
                        if rdiff != 0:
                            token = rtoken
                        ntoken = token.translate(stopchars)
                        ndiff = len(token) - len(ntoken)
                        if ndiff:
                            token = ntoken
                        if not token:
                            start_char += 1
                            continue

                        is_enclitic = False
                        if token not in exceptions:
                            if t.original in replacements:
                                for subtoken in replacements[t.original]:
                                    t.text = subtoken
                                    t.startchar = start_char
                                    t.endchar = start_char + original_length
                                    if mode == 'index': self._cache.append(copy.copy(t))
                                    yield t
                                start_char += original_length + 1
                                continue

                            if re.match(r"(?:\w+) (?:\w+)", token):
                                ppp, copula = token.split(' ')
                                t.text = ppp.lower()
                                t.startchar = start_char
                                t.endchar = start_char + len(ppp)
                                if mode == 'index': self._cache.append(copy.copy(t))
                                yield t
                                t.text = copula.lower()
                                t.startchar = start_char + len(ppp) + 1
                                t.endchar = start_char + len(ppp) + 1 + len(copula)
                                if mode == 'index': self._cache.append(copy.copy(t))
                                yield t
                                start_char += original_length + 1
                                continue

                            for enclitic in enclitics:
                                if token.lower().endswith(enclitic):
                                    if enclitic == 'ne':
                                        t.text = (token[:-len(enclitic)]).lower()
                                        t.startchar = start_char
                                        t.endchar = start_char + (len(token) - len(enclitic))
                                        if mode == 'index': self._cache.append(copy.copy(t))
                                        yield t
                                        t.text = 'ne'
                                        t.startchar = start_char + len(token[:-len(enclitic)])
                                        t.endchar = start_char + len(token[:-len(enclitic)]) + len(enclitic)
                                        if mode == 'index': self._cache.append(copy.copy(t))
                                        yield t
                                    elif enclitic == 'n':
                                        t.text = (token[:-len(enclitic)] + 's').lower()
                                        t.startchar = start_char
                                        t.endchar = start_char + (len(token) + 1) - len(enclitic)
                                        if mode == 'index': self._cache.append(copy.copy(t))
                                        yield t
                                        t.text = 'ne'
                                        t.startchar = start_char + len(token[:-len(enclitic)])
                                        t.endchar = start_char + len(token[:-len(enclitic)]) + len(enclitic)
                                        if mode == 'index': self._cache.append(copy.copy(t))
                                        yield t
                                    elif enclitic == 'st':
                                        if token.endswith('ust'):
                                            t.text = (token[:-len(enclitic) + 1]).lower()
                                            t.startchar = start_char
                                            t.endchar = start_char + len(token[:-len(enclitic) + 1]) - len(enclitic)
                                            if mode == 'index': self._cache.append(copy.copy(t))
                                            yield t
                                            t.text = 'est'
                                            t.startchar = start_char + len(token[:-len(enclitic) + 1])
                                            t.endchar = start_char + len(token[:-len(enclitic) + 1]) + len(enclitic)
                                            if mode == 'index': self._cache.append(copy.copy(t))
                                            yield t
                                        else:
                                            t.text = (token[:-len(enclitic)]).lower()
                                            t.startchar = start_char
                                            t.endchar = start_char + len(token[:-len(enclitic)]) - len(enclitic)
                                            if mode == 'index': self._cache.append(copy.copy(t))
                                            yield t
                                            t.text = 'est'
                                            t.startchar = start_char + len(token[:-len(enclitic) + 1])
                                            t.endchar = start_char + len(token[:-len(enclitic) + 1]) + len(enclitic)
                                            if mode == 'index': self._cache.append(copy.copy(t))
                                            yield t
                                    elif enclitic == "'s":
                                        t.text = token + 's'
                                        t.startchar = start_char
                                        t.endchar = start_char + len(token)
                                        if mode == 'index': self._cache.append(copy.copy(t))
                                        yield t
                                        t.text = 'es'
                                        t.startchar = start_char + len(token) + 1
                                        t.endchar = start_char + len(token) + len(enclitic)
                                        if mode == 'index': self._cache.append(copy.copy(t))
                                        yield t
                                    else:
                                        t.text = (token[:-len(enclitic)])
                                        t.startchar = start_char
                                        t.endchar = start_char + len(token[:-len(enclitic)])
                                        if mode == 'index': self._cache.append(copy.copy(t))
                                        yield t
                                        t.text = enclitic
                                        t.startchar = start_char + len(token[:-len(enclitic)])
                                        t.endchar = start_char + len(token[:-len(enclitic)]) + len(enclitic)
                                        if mode == 'index': self._cache.append(copy.copy(t))
                                        yield t
                                    is_enclitic = True
                                    break
                        if not is_enclitic:
                            t.text = token
                            if chars:
                                t.startchar = start_char + ldiff
                                t.endchar = start_char + original_length - rdiff  # - ndiff - rdiff
                            if mode == 'index': self._cache.append(copy.copy(t))
                            yield t
                        start_char += original_length + 1

Tokens = CachedTokenizer(chars=True)
Lemmas = CachedLemmaFilter(chars=True)
Synsets = CachedSynsetFilter()
Annotations = AnnotationFilter()
Semfields = SemfieldFilter()


class DocumentSchema(BaseSchema):
    content = STORED()
    form = FORM(analyzer=Tokens, vector=True)
    lemma = LEMMA(analyzer=Tokens | Lemmas, vector=True)
    annotation = ANNOTATION(analyzer=Tokens | Lemmas | Annotations, vector=True)
    synset = SYNSET(analyzer=Tokens | Lemmas | Synsets, vector=True)
    semfield = SEMFIELD(analyzer=Tokens | Lemmas | Synsets | Semfields, vector=True)


# Fetch function for generic plaintext corpora
def fetch(hit, meta, fragment):
    content = hit['content']
    offset = content.find(fragment)

    # Reference and hlite values
    start = ', '.join(
        [f"{k}: {v}" for k, v in meta['start'].items() if v]
    )
    end = ', '.join(
        [f"{k}: {v}" for k, v in meta['end'].items() if v]
    )
    reference = '-'.join([start, end]) if end != start else start
    hlite_start = [
        v - offset
        if k != 'pos' and v is not None else v
        for k, v in meta['start'].items()
    ]

    # Collect text and context
    lbound = fragment.rfind(' ', 0, settings.CHARS_OF_CONTEXT)
    rbound = fragment.find(' ', -(settings.CHARS_OF_CONTEXT - (meta['start']['endchar'] - meta['start']['startchar'])))

    pre = f"<pre>{fragment[:lbound]}</pre>"
    post = f"<post>{fragment[rbound + 1:]}</post>"

    endchar = lbound + 1 + (hlite_start[-2] - hlite_start[-3])
    hlite = f"<em>{fragment[lbound + 1:endchar]}</em>" + fragment[endchar:rbound]
    match = f"<match>{hlite}</match>"

    text = f' '.join([pre, match, post])
    return None, reference, text
