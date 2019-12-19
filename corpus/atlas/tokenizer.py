import copy

from engine.analysis.tokenizers import Tokenizer
from engine.analysis.acore import CylleneusToken
from corpus.agldt import agldt2wn


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

    def __call__(
        self,
        data,
        positions=True,
        chars=True,
        keeporiginal=True,
        removestops=True,
        tokenize=True,
        start_pos=0,
        start_char=0,
        mode="",
        **kwargs,
    ):
        if kwargs.get("docix", None) == self._docix and self._cache:
            yield from self.cache
        else:
            t = CylleneusToken(
                positions, chars, removestops=removestops, mode=mode, **kwargs
            )

            if t.mode == "query":
                t.original = t.text = data
                yield t
            else:
                self._cache = []
                self._docix = kwargs.get("docix", None)

                if not tokenize:
                    t.original = ""
                    for token in data["text"].iter("token"):
                        form = token.get("form")
                        if not form:
                            continue
                        t.original += f"{form}"
                    t.text = t.original
                    t.boost = 1.0
                    if positions:
                        t.pos = start_pos
                    if chars:
                        t.startchar = start_char
                        t.endchar = start_char + len(t.original)
                    yield t
                else:
                    for sentence in data["text"].iter("sentence"):
                        sect_pos = -1
                        curr_line = None
                        for pos, token in enumerate(sentence.iter("word")):
                            if token.get("artificial", False):
                                continue

                            form = token.get("form")
                            if not form:
                                continue
                            t.text = form

                            lemma = token.get("lemma")
                            if not lemma or lemma in ("???", ".", ",", ";", "·", "punc1", "comma1", "PERIOD1"):
                                continue
                            t.lemma = lemma

                            t.morpho = agldt2wn(token.get("postag"))
                            t.morphosyntax = token.get("relation", None)
                            t.boost = 1.0

                            meta = {"meta": data["meta"].lower()}
                            divs = data["meta"].split("-")

                            refs = (
                                token.get("cite")
                                    .rsplit(":", maxsplit=1)[1]
                                    .split(".")
                            )
                            for i, div in enumerate(divs):
                                meta[div] = refs[i]
                            meta["sent_id"] = sentence.get("id")
                            meta["sent_pos"] = str(int(token.get("id")))

                            if curr_line and refs[-1] > curr_line:
                                sect_pos = 0
                            else:
                                sect_pos += 1
                            curr_line = refs[-1]

                            meta["sect_pos"] = sect_pos  # ref in line
                            t.meta = meta

                            if keeporiginal:
                                t.original = f"{form}"
                            t.stopped = False
                            if positions:
                                t.pos = start_pos + pos
                            original_len = len(form)

                            if chars:
                                t.startchar = start_char
                                t.endchar = start_char + original_len
                            if self.cached:
                                self._cache.append(copy.copy(t))
                            yield t

                            start_char += len(form)
