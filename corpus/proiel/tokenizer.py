import copy
import re

from engine.analysis.tokenizers import Tokenizer
from engine.analysis.acore import CylleneusToken
from lang.latin import editorial, jvmap


class CachedTokenizer(Tokenizer):
    def __init__(self, **kwargs):
        super(CachedTokenizer, self).__init__()
        self.__dict__.update(**kwargs)
        self._cache = None
        self._docix = None

    @property
    def cache(self):
        return copy.deepcopy(self._cache)

    def __call__(self, data, positions=True, chars=True,
                 keeporiginal=True, removestops=True, tokenize=True,
                 start_pos=0, start_char=0, mode='', **kwargs):
        if kwargs.get('docix', None) == self._docix and self._cache:
            yield from self.cache
        else:
            self._cache = []
            self._docix = kwargs.get('docix', None)

            t = CylleneusToken(positions, chars, removestops=removestops, mode=mode, **kwargs)
            if t.mode == 'query':
                t.original = t.text = data.translate(jvmap)
                yield t
            else:
                if not tokenize:
                    t.original = ''
                    for token in data.findall('.//token'):
                        form = token.get('form')
                        if not form:
                            continue
                        after = token.get('presentation-after', '')
                        before = token.get('presentation-before', '')
                        t.original += f"{before}{form}{after}"
                    t.text = t.original
                    t.boost = 1.0
                    if positions:
                        t.pos = start_pos
                    if chars:
                        t.startchar = start_char
                        t.endchar = start_char + len(t.original)
                    yield t
                else:
                    from corpus.proiel import parse_proiel

                    for sentence in data['text'].findall('.//sentence'):
                        for pos, token in enumerate(sentence.findall('.//token')):
                            form = token.get('form')
                            if not form:
                                continue
                            else:
                                form = form.replace(' ', ' ').replace(' ', ' ')
                                form = re.sub(r"\.([^ ]|^$)", r'. \1', form)
                            t.lemma = token.get('lemma')
                            t.morpho = parse_proiel(token.get('part-of-speech'), token.get('morphology'))
                            t.morphosyntax = token.get('relation', None)
                            t.boost = 1.0

                            meta = {
                                'meta': data['meta'].lower()
                            }
                            for i, div in enumerate(data['meta'].split('-')):
                                meta[div] = token.get('citation-part').split('.')[i]
                            meta['sent_id'] = sentence.get('id')
                            meta['sent_pos'] = token.get('id')
                            t.meta = meta

                            before = token.get('presentation-before', '')
                            after = token.get('presentation-after', '')

                            if keeporiginal:
                                t.original = f"{before}{form}{after}"
                            t.stopped = False
                            if positions:
                                t.pos = start_pos + pos
                            original_len = len(form)

                            if form.istitle() and pos == 0 and not t.lemma.istitle():
                                form = form.lower()
                            t.text = form
                            if chars:
                                t.startchar = start_char + len(before)
                                t.endchar = start_char + len(before) + original_len
                            self._cache.append(copy.deepcopy(t))
                            yield t

                            if form in editorial:
                                t.text = editorial[form]
                                self._cache.append(copy.deepcopy(t))
                                yield t
                            start_char += len(before) + len(form) + len(after)

