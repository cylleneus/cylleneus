import copy
import re

from cylleneus.engine.analysis.tokenizers import Tokenizer
from cylleneus.engine.analysis.acore import CylleneusToken
from cylleneus.lang.lat import editorial, jvmap
from cylleneus.corpus.lat.agldt import agldt2wn


class CachedTokenizer(Tokenizer):
    def __init__(self, cached=True, **kwargs):
        super(CachedTokenizer, self).__init__()
        self.cached = cached
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
                t.original = data
                t.text = data.translate(jvmap)
                yield t
            else:
                self._cache = []
                self._docix = kwargs.get("docix", None)

                if tokenize:
                    for sentence in data["text"].iter("sentence"):
                        for pos, token in enumerate(sentence.iter("word")):
                            if token.get("artificial", False):
                                continue
                            form = token.get("form")
                            if form:
                                form = form.replace(" ", " ").replace(" ", " ")
                                form = re.sub(r"\.([^ ]|^$)", r". \1", form)
                            else:
                                continue
                            lemma = token.get("lemma", None)
                            if not lemma or lemma in (
                                ".",
                                ",",
                                "punc1",
                                "comma1",
                                "PERIOD1",
                            ):
                                continue
                            t.lemma = lemma.strip("0123456789")
                            t.morpho = agldt2wn(token.get("postag"))
                            t.morphosyntax = token.get("relation", None)
                            t.boost = 1.0

                            meta = {"meta": data["meta"].lower()}
                            divs = data["meta"].split("-")
                            for i, div in enumerate(divs):
                                if len(divs) <= 2 or div != "line":
                                    meta[div] = sentence.get("subdoc").split(
                                        "."
                                    )[i]
                            meta["sent_id"] = sentence.get("id")
                            meta["sent_pos"] = token.get("id")
                            t.meta = meta

                            if keeporiginal:
                                t.original = f"{form}"
                            t.stopped = False
                            if positions:
                                t.pos = copy.copy(start_pos + pos)
                            original_len = len(form)

                            if (
                                form.istitle()
                                and pos == 0
                                and not t.lemma.istitle()
                            ):
                                form = form.lower()
                            t.text = form
                            if chars:
                                t.startchar = copy.copy(start_char)
                                t.endchar = copy.copy(start_char + original_len)
                            if self.cached:
                                self._cache.append(copy.deepcopy(t))
                            yield t

                            if form in editorial:
                                t.text = editorial[form]
                                if self.cached:
                                    self._cache.append(copy.copy(t))
                                yield t
                            start_char += len(form)
                else:
                    t.original = ""
                    for token in data.iter("token"):
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
