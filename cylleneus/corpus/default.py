import codecs
import copy
import string
from datetime import datetime
from pathlib import Path

from cylleneus import settings
from cylleneus.corpus.preprocessing import BasePreprocessor
from cylleneus.engine.analysis.acore import CylleneusToken
from cylleneus.engine.analysis.filters import AnnotationFilter, CachedLemmaFilter, CachedSynsetFilter, \
    SemfieldFilter
from cylleneus.engine.analysis.tokenizers import Tokenizer
from cylleneus.engine.fields import *
from cylleneus.engine.schemas import BaseSchema
from cylleneus.lang.lat import convert_diphthongs, jvmap, sent_tokenizer, word_tokenizer, strip_diacritics
from cylleneus.utils import autotrim

# Description
description = "Default plaintext corpus"

# Language
language = ""

# Glob pattern
glob = '*.txt'


class Preprocessor(BasePreprocessor):
    def parse(self, file: Path):
        with codecs.open(file, 'r', 'utf8') as fp:
            doc = fp.read()

        # Basic text cleaning
        doc = re.sub(r'(\s)+', r'\1', doc)

        return {
            'content': doc,
            'form': doc,
            'lemma': doc,
            'synset': doc,
            'annotation': doc,
            'semfield': doc,
            'filename': file.name,
            'datetime': datetime.datetime.now()
        }


class CachedTokenizer(Tokenizer):
    def __init__(self, **kwargs):
        super(CachedTokenizer, self).__init__()
        self.cached = True
        self._cache = None
        self._docix = None
        self.__dict__.update(**kwargs)

    @property
    def cache(self):
        return copy.deepcopy(self._cache)

    def __call__(self, value: str, positions=True, chars=True,
                 keeporiginal=True, removestops=True, tokenize=True,
                 start_pos=0, start_char=0, mode='', **kwargs):
        if kwargs.get('docix') == self._docix and self._cache:
            yield from self.cache
        else:
            t = CylleneusToken(positions, chars, removestops=removestops, mode=mode, **kwargs)

            stopchars = "!\"#$%()*+,-—./:;<=>?@[\]^_`{|}~"
            punctuation = str.maketrans('', '', stopchars)

            if t.mode == 'query':
                t.original = t.text = value.translate(jvmap)
                yield t
            else:
                if not tokenize:
                    # Assume value is a list
                    for pos, token in enumerate(value):
                        t.original = t.text = token
                        t.boost = 1.0
                        if positions:
                            t.pos = pos
                        if chars:
                            t.startchar = start_char
                            t.endchar = start_char + len(token)
                            start_char += len(token)
                        yield t
                else:
                    self._cache = []
                    self._docix = kwargs.get('docix', None)

                    work_pos = 0
                    for i, sentence in enumerate(sent_tokenizer.tokenize(value)):
                        sent_pos = 0
                        for token in word_tokenizer.word_tokenize(sentence):
                            if token in string.whitespace:
                                start_char += 1
                                continue
                            t.boost = 1.0
                            if keeporiginal:
                                t.original = token
                            original_length = len(token)
                            t.stopped = False

                            token = convert_diphthongs(strip_diacritics(token)).translate(jvmap)
                            if token in stopchars:
                                start_char += original_length
                                continue
                            t.text = token.translate(punctuation)

                            if positions:
                                t.pos = start_pos + work_pos
                            if chars:
                                t.startchar = start_char
                                t.endchar = start_char + original_length
                            t.meta = {
                                'sent_id':  i,
                                'sent_pos': sent_pos
                            }
                            if mode == 'index':
                                if self.cached: self._cache.append(copy.copy(t))
                            yield t

                            work_pos += 1
                            sent_pos += 1
                            start_char += original_length
                        start_char += 1


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


# Fetch function for plaintext corpora with content
def fetch(work, meta, fragment):
    content = work.doc['content']
    content = re.sub(r'(\s)+', r'\1', content)

    # Reference and hlite values
    start = ', '.join(
        [f"{k}: {v}" for k, v in meta['start'].items() if v]
    )
    end = ', '.join(
        [f"{k}: {v}" for k, v in meta['end'].items() if v]
    )
    reference = '-'.join([start, end]) if end != start else start

    hlite_starts = [
        startchar
        for startchar, endchar, pos in meta['hlites']
    ]
    hlite_ends = [
        endchar
        for startchar, endchar, pos in meta['hlites']
    ]

    # Collect text and context
    pre_raw = content[hlite_starts[0] - settings.CHARS_OF_CONTEXT:hlite_starts[0]]
    pre = f"<pre>{autotrim(pre_raw, right=False)}</pre>"

    post_raw = content[hlite_ends[-1] + 1:hlite_ends[-1] + settings.CHARS_OF_CONTEXT]
    post = f"<post>{autotrim(post_raw, left=False)}</post>"

    match_raw = content[hlite_starts[0]:hlite_ends[-1] + 1]
    hlite = ''
    if len(hlite_starts) == 1 and len(hlite_ends) == 1:
        hlite = f"<em>{match_raw}</em>"
    else:
        cursor = hlite_starts[0]
        for c in match_raw:
            if cursor in hlite_starts:
                hlite += '<em>' + c
            elif cursor in hlite_ends:
                hlite += '</em>' + c
            else:
                hlite += c
            cursor += 1
        if cursor in hlite_ends:
            hlite += '</em>'
    match = f"<match>{hlite}</match>"

    text = f''.join([pre, match, post])
    urn = work.urn

    return urn, reference, text


repo = {
    'origin':   None,
    'location': 'local'
}
