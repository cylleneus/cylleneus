import copy
import string

from engine.analysis.acore import CylleneusToken
from engine.analysis.tokenizers import Tokenizer
from nltk.tokenize import word_tokenize
from utils import flatten, stringify


class CachedTokenizer(Tokenizer):
    def __init__(self, **kwargs):
        super(CachedTokenizer, self).__init__()
        self._cache = None
        self._docix = None
        self.cached = True
        self.__dict__.update(**kwargs)

    @property
    def cache(self):
        return copy.deepcopy(self._cache)

    def __call__(self, value, positions=True, chars=True,
                 keeporiginal=True, removestops=True, tokenize=True,
                 start_pos=0, start_char=0, mode='', **kwargs):
        if kwargs.get('docix', None) == self._docix and self._cache is not None:
            yield from self.cache
        else:
            t = CylleneusToken(positions, chars, removestops=removestops, mode=mode, **kwargs)
            if t.mode == 'query':
                t.original = t.text = value
                yield t
            else:
                if not tokenize:
                    text = '\n'.join([el for el in flatten(value['text'])])
                    t.original = t.text = text
                    t.boost = 1.0
                    if positions:
                        t.pos = start_pos
                    if chars:
                        t.startchar = start_char
                        t.endchar = start_char + len(text)
                    yield t
                else:
                    self._cache = []
                    self._docix = kwargs.get('docix', None)

                    tokenizer = word_tokenize
                    stopchars = string.punctuation

                    doc = value['text']
                    divs = [
                        cref.get('n')
                        for cref in reversed(doc.findall(".//{http://www.tei-c.org/ns/1.0}cRefPattern"))
                    ]
                    tei_base = "/tei:TEI/tei:text/tei:body/tei:div"

                    # lines = doc.xpath(
                    #     tei_base + ("/tei:div" * len(divs)) + "/tei:p/tei:s",
                    #     namespaces={
                    #         'tei': 'http://www.tei-c.org/ns/1.0'
                    #     }
                    # )
                    ss = doc.findall(
                        ".//{http://www.tei-c.org/ns/1.0}s"
                    )

                    for n, s in enumerate(ss):
                        meta = {
                            'meta':    '-'.join(divs),
                            'sent_id': s.get('{http://www.w3.org/XML/1998/namespace}id'),
                            'align':   s.get('n')
                        }

                        el = s
                        j = 0
                        while el is not None:
                            if el.getparent() is not None:
                                if el.getparent().get('type', None) == 'textpart':
                                    j -= 1
                                    meta[divs[j]] = el.getparent().get('n')
                            el = el.getparent()

                        text = stringify(s)

                        pos = 0
                        for i, token in enumerate(tokenizer(text)):
                            if token == ' ' or token in stopchars:
                                pos -= 1
                                continue

                            t.boost = 1.0
                            if keeporiginal:
                                t.original = token
                            t.stopped = False

                            if positions:
                                t.pos = start_pos + pos
                            meta['sent_pos'] = pos

                            length = len(token)

                            token = token.strip()
                            if not token:
                                start_char += length
                                continue

                            t.meta = copy.deepcopy(meta)

                            t.text = token
                            if chars:
                                t.startchar = start_char
                                t.endchar = start_char + length
                            if mode == 'index':
                                self._cache.append(copy.deepcopy(t))
                            yield t
                            start_char += length

                            pos += 1
                        start_char += 1
