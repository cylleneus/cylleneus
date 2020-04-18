import copy
import re
import string

from cylleneus.engine.analysis.acore import CylleneusToken
from cylleneus.engine.analysis.tokenizers import Tokenizer
from cylleneus.lang.lat import enclitics, jvmap, word_tokenizer


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
        **kwargs
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

                if not tokenize:
                    t.original = ""
                    for el in data["text"].find("text").find("body").iter():
                        if el.tag in ["head", "p", "l"]:
                            if not el.text:
                                text = "".join(
                                    [
                                        subel.text + subel.tail
                                        for subel in el.iter()
                                        if subel.tag != el.tag
                                    ]
                                )
                            else:
                                text = el.text
                            subs = [
                                r"<note>(.*?)</note>",
                                r'<sic corr="(\w+?)">\w+?</sic>',
                                r'<reg orig="\w+?">(\w+?)</reg>',
                            ]
                            for sub in subs:
                                text = re.sub(sub, "\1", text)
                            t.original += text
                    t.text = t.original
                    t.boost = 1.0
                    if positions:
                        t.pos = start_pos
                    if chars:
                        t.startchar = start_char
                        t.endchar = start_char + len(t.original)
                    yield t
                else:
                    punc = str.maketrans("", "", string.punctuation)

                    tags = data["meta"].split("-")
                    meta = {"meta": data["meta"].lower()}
                    meta.update({tag: "-" for tag in tags})

                    divs = ["div1", "div2", "div3", "div4", "div5"]

                    sect_sent = 0
                    sect_pos = 0
                    sent_id = 0
                    pos = 0

                    for el in data["text"].find("text").find("body").iter():
                        if el.tag in divs:
                            current_div_ix = divs.index(el.tag)
                            meta[tags[current_div_ix]] = el.get("n", "-")
                            sect_sent = 0
                            sect_pos = 0
                        elif el.tag in ["head", "p", "l"]:
                            sent_id += 1
                            sect_sent += 1
                            if not el.text:
                                text = "".join(
                                    [
                                        subel.text + subel.tail
                                        for subel in el.iter()
                                        if subel.tag != el.tag
                                    ]
                                )
                            else:
                                text = el.text
                            subs = [
                                r"<note>(.*?)</note>",
                                r'<sic corr="(\w+?)">\w+?</sic>',
                                r'<reg orig="\w+?">(\w+?)</reg>',
                            ]
                            for sub in subs:
                                text = re.sub(sub, "\1", text)

                            tokens = word_tokenizer.word_tokenize(text)
                            for i, token in enumerate(tokens):
                                pos += 1
                                sect_pos += 1

                                t.text = token.translate(punc).lower().translate(jvmap)
                                if not t.text or t.text in string.whitespace:
                                    start_char += 1
                                    continue

                                t.boost = 1.0

                                meta["sent_id"] = sent_id
                                meta["sent_pos"] = i
                                meta["sect_sent"] = sect_sent
                                meta["sect_pos"] = sect_pos

                                t.meta = copy.copy(meta)

                                if keeporiginal:
                                    t.original = token
                                t.stopped = False
                                if positions:
                                    t.pos = start_pos + pos

                                is_enclitic = False
                                for enclitic in enclitics:
                                    if token.endswith(enclitic):
                                        if enclitic == "ne":
                                            t.text = token[: -len(enclitic)]
                                            t.startchar = start_char
                                            t.endchar = start_char + (
                                                len(token) - len(enclitic)
                                            )
                                            if mode == "index":
                                                self._cache.append(copy.deepcopy(t))
                                            yield t
                                            t.text = "ne"
                                            t.startchar = start_char + len(
                                                token[: -len(enclitic)]
                                            )
                                            t.endchar = (
                                                start_char
                                                + len(token[: -len(enclitic)])
                                                + len(enclitic)
                                            )
                                            if mode == "index":
                                                self._cache.append(copy.deepcopy(t))
                                            yield t
                                        elif enclitic == "n":
                                            t.text = token[: -len(enclitic)] + "s"
                                            t.startchar = start_char
                                            t.endchar = (
                                                start_char + len(token) - len(enclitic)
                                            )
                                            if mode == "index":
                                                self._cache.append(copy.deepcopy(t))
                                            yield t
                                            t.text = "ne"
                                            t.startchar = start_char + len(
                                                token[: -len(enclitic)]
                                            )
                                            t.endchar = (
                                                start_char
                                                + len(token[: -len(enclitic)])
                                                + len(enclitic)
                                            )
                                            if mode == "index":
                                                self._cache.append(copy.deepcopy(t))
                                            yield t
                                        elif enclitic == "st":
                                            if token.endswith("ust"):
                                                t.text = token[: -len(enclitic)]
                                                t.startchar = start_char
                                                t.endchar = (
                                                    start_char
                                                    + len(token[: -len(enclitic)])
                                                    - len(enclitic)
                                                )
                                                if mode == "index":
                                                    self._cache.append(copy.deepcopy(t))
                                                yield t
                                                t.text = "est"
                                                t.startchar = start_char + len(
                                                    token[: -len(enclitic)]
                                                )
                                                t.endchar = (
                                                    start_char
                                                    + len(token[: -len(enclitic)])
                                                    + len(enclitic)
                                                )
                                                if mode == "index":
                                                    self._cache.append(copy.deepcopy(t))
                                                yield t
                                            else:
                                                t.text = token[: -len(enclitic)]
                                                t.startchar = start_char
                                                t.endchar = (
                                                    start_char
                                                    + len(token[: -len(enclitic)])
                                                    - len(enclitic)
                                                )
                                                if mode == "index":
                                                    self._cache.append(copy.deepcopy(t))
                                                yield t
                                                t.text = "est"
                                                t.startchar = start_char + len(
                                                    token[: -len(enclitic)]
                                                )
                                                t.endchar = (
                                                    start_char
                                                    + len(token[: -len(enclitic)])
                                                    + len(enclitic)
                                                )
                                                if mode == "index":
                                                    self._cache.append(copy.deepcopy(t))
                                                yield t
                                        elif enclitic == "'s":
                                            t.text = token + "s"
                                            t.startchar = start_char
                                            t.endchar = start_char + len(token)
                                            if mode == "index":
                                                self._cache.append(copy.deepcopy(t))
                                            yield t
                                            t.text = "es"
                                            t.startchar = start_char + len(token) + 1
                                            t.endchar = (
                                                start_char + len(token) + len(enclitic)
                                            )
                                            if mode == "index":
                                                self._cache.append(copy.deepcopy(t))
                                            yield t
                                        else:
                                            t.text = token[: -len(enclitic)]
                                            t.startchar = start_char
                                            t.endchar = start_char + len(
                                                token[: -len(enclitic)]
                                            )
                                            if mode == "index":
                                                self._cache.append(copy.deepcopy(t))
                                            yield t
                                            t.text = enclitic
                                            t.startchar = start_char + len(
                                                token[: -len(enclitic)]
                                            )
                                            t.endchar = (
                                                start_char
                                                + len(token[: -len(enclitic)])
                                                + len(enclitic)
                                            )
                                            if mode == "index":
                                                self._cache.append(copy.deepcopy(t))
                                            yield t
                                        is_enclitic = True
                                        break

                                if not is_enclitic:
                                    original_len = len(token)
                                    if chars:
                                        t.startchar = start_char
                                        t.endchar = start_char + original_len
                                    if self.cached:
                                        self._cache.append(copy.copy(t))
                                    yield t

                                start_char += len(token)
