import copy
import re

from cylleneus.engine.analysis.tokenizers import Tokenizer
from cylleneus.engine.analysis.acore import CylleneusToken
from cylleneus.lang.lat import editorial, jvmap
from .core import proiel2wn


class CachedTokenizer(Tokenizer):
    def __init__(self, cached=True, **kwargs):
        super(CachedTokenizer, self).__init__()
        self._cache = None
        self._docix = None
        self.cached = cached
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
                if not tokenize:
                    t.original = ""
                    for token in data.iter("token"):
                        form = token.get("form")
                        if not form:
                            continue
                        after = token.get("presentation-after", "")
                        before = token.get("presentation-before", "")
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
                    self._cache = []
                    self._docix = kwargs.get("docix", None)

                    for sentence in data["text"].iter("sentence"):
                        for pos, token in enumerate(sentence.iter("token")):
                            form = token.get("form")
                            if not form:
                                continue
                            else:
                                form = form.replace(" ", " ").replace(" ", " ")
                                form = re.sub(r"\.([^ ]|^$)", r". \1", form)
                            t.lemma = token.get("lemma")
                            t.morpho = proiel2wn(
                                token.get("part-of-speech"),
                                token.get("morphology"),
                            )
                            t.morphosyntax = token.get("relation", None)
                            t.boost = 1.0

                            meta = {"meta": data["meta"].lower()}
                            for i, div in enumerate(data["meta"].split("-")):
                                meta[div] = token.get("citation-part").split(
                                    "."
                                )[i]
                            meta["sent_id"] = sentence.get("id")
                            meta["sent_pos"] = token.get("id")
                            t.meta = meta

                            before = token.get("presentation-before", "")
                            after = token.get("presentation-after", "")

                            if keeporiginal:
                                t.original = f"{before}{form}{after}"
                            t.stopped = False
                            if positions:
                                t.pos = start_pos + pos
                            original_len = len(form)

                            if (
                                form.istitle()
                                and pos == 0
                                and not t.lemma.istitle()
                            ):
                                form = form.lower()
                            t.text = form
                            if chars:
                                t.startchar = start_char + len(before)
                                t.endchar = (
                                    start_char + len(before) + original_len
                                )
                            self._cache.append(copy.deepcopy(t))
                            yield t

                            if form in editorial:
                                t.text = editorial[form]
                                self._cache.append(copy.deepcopy(t))
                                yield t
                            start_char += len(before) + len(form) + len(after)
