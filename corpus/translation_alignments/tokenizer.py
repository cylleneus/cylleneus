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

    def __call__(
        self,
        value,
        positions=True,
        chars=True,
        keeporiginal=True,
        removestops=True,
        tokenize=True,
        start_pos=0,
        start_char=0,
        mode="",
        **kwargs
    ):
        if kwargs.get("docix", None) == self._docix and self._cache is not None:
            yield from self.cache
        else:
            t = CylleneusToken(
                positions, chars, removestops=removestops, mode=mode, **kwargs
            )
            if t.mode == "query":
                t.original = t.text = value
                yield t
            else:
                if not tokenize:
                    text = "\n".join([el for el in flatten(value["text"])])
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
                    self._docix = kwargs.get("docix", None)

                    tokenizer = word_tokenize
                    stopchars = string.punctuation

                    doc = value["text"]
                    divs = [
                        cref.get("n")
                        for cref in reversed(
                            doc.findall(".//{http://www.tei-c.org/ns/1.0}cRefPattern")
                        )
                    ]

                    ss = doc.findall(".//{http://www.tei-c.org/ns/1.0}s")

                    sect_sent = 0
                    sect_pos = 0
                    for n, s in enumerate(ss):
                        meta = {
                            "meta":      "-".join(divs),
                            "sent_id":   s.get(
                                "{http://www.w3.org/XML/1998/namespace}id"
                            ),
                            "sect_sent": sect_sent,
                            "alignment": s.get("n"),
                        }

                        el = s
                        j = 0
                        while el is not None:
                            if el.getparent() is not None:
                                if el.getparent().get("type", None) == "textpart":
                                    j -= 1
                                    if divs[j] in meta and el.getparent().get("n") != meta[divs[j]]:
                                        sect_sent = 0
                                        sect_pos = 0
                                    meta[divs[j]] = el.getparent().get("n")
                            el = el.getparent()

                        text = stringify(s)

                        sent_pos = 0
                        for i, token in enumerate(tokenizer(text)):
                            if token == " " or token in stopchars:
                                sect_pos += 1
                                sent_pos += 1
                                continue

                            t.boost = 1.0
                            if keeporiginal:
                                t.original = token
                            t.stopped = False

                            meta["sent_pos"] = sent_pos
                            meta["sect_pos"] = sect_pos
                            if positions:
                                t.pos = start_pos + sect_pos

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
                            if mode == "index":
                                self._cache.append(copy.deepcopy(t))
                            yield t

                            start_char += length
                            sect_pos += 1
                            sent_pos += 1
                        sect_sent += 1
                        start_char += 1
