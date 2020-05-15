import copy
import re
import string

from cylleneus.engine.analysis.acore import CylleneusToken
from cylleneus.engine.analysis.tokenizers import Tokenizer
from cylleneus.lang.lat import (
    enclitics,
    jvmap,
    latin_exceptions,
    sent_tokenizer,
    word_tokenizer,
)


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

                    tags = data["meta"].lower()
                    meta = {"meta": tags}
                    if tags != "-":
                        divs = data["meta"].split("-")
                        meta.update({div: "-" for div in divs})

                    sect_sent = 0
                    sect_pos = 0
                    sent_id = 0
                    pos = 0

                    for el in (
                        data["text"]
                            .find("{http://www.tei-c.org/ns/1.0}text")
                            .find("{http://www.tei-c.org/ns/1.0}body")
                            .findall(".//{http://www.tei-c.org/ns/1.0}*")
                    ):
                        if el.tag == "{http://www.tei-c.org/ns/1.0}milestone":
                            meta[el.get("unit")] = el.get("n", "-")
                            sect_sent = 0
                            sect_pos = 0
                        elif (
                            el.tag == "{http://www.tei-c.org/ns/1.0}div"
                            and el.get("n")
                        ):
                            meta[el.get("type")] = el.get("n", "-")
                            sect_sent = 0
                            sect_pos = 0

                        if not el.text:
                            text = el.tail if el.tail else ""
                        else:
                            text = el.text + (el.tail if el.tail else "")
                        subs = [
                            (r"<supplied>(.*?)</supplied>", "\1"),
                            (r'<quote type="\w+?">(.+?)</quote>', "\1"),
                            (r'<hi rend="\w+?">(.+?)</hi>', "\1"),
                            (r'<g ref="\w+?">(.+?)</g>', "\1"),
                            (
                                r'<foreign xml:lang="\w+?">(\w+?)</foreign>',
                                "\1",
                            ),
                            (r"<del>.+?</del>", ""),
                        ]
                        for old, new in subs:
                            text = re.sub(old, new, text)

                        if text:
                            for sentence in sent_tokenizer.tokenize(text):
                                sent_id += 1
                                sect_sent += 1

                                sentence = sentence.strip()
                                replacements = [(r"\n", ""), (r"\s+", " ")]
                                for old, new in replacements:
                                    sentence = re.sub(old, new, sentence)

                                sent_pos = 0
                                tokens = word_tokenizer.word_tokenize(sentence)

                                for token in tokens:
                                    token = (
                                        token.translate(punc)
                                            .lower()
                                            .translate(jvmap)
                                            .strip()
                                    )

                                    if not token or token in string.whitespace:
                                        start_char += 1
                                        continue
                                    else:
                                        pos += 1
                                        sect_pos += 1
                                        sent_pos += 1

                                        t.text = token
                                        t.boost = 1.0

                                        meta["sent_id"] = sent_id
                                        meta["sent_pos"] = sent_pos
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
                                            if (
                                                token.endswith(enclitic)
                                                and token
                                                not in latin_exceptions
                                            ):
                                                if enclitic == "ne":
                                                    t.text = token[
                                                             : -len(enclitic)
                                                             ]
                                                    t.startchar = start_char
                                                    t.endchar = start_char + (
                                                        len(token)
                                                        - len(enclitic)
                                                    )
                                                    if mode == "index":
                                                        self._cache.append(
                                                            copy.deepcopy(t)
                                                        )
                                                    yield t
                                                    t.text = "ne"
                                                    t.startchar = (
                                                        start_char
                                                        + len(
                                                        token[
                                                        : -len(
                                                            enclitic
                                                        )
                                                        ]
                                                    )
                                                    )
                                                    t.endchar = (
                                                        start_char
                                                        + len(
                                                        token[
                                                        : -len(
                                                            enclitic
                                                        )
                                                        ]
                                                    )
                                                        + len(enclitic)
                                                    )
                                                    if mode == "index":
                                                        self._cache.append(
                                                            copy.deepcopy(t)
                                                        )
                                                    yield t
                                                elif enclitic == "n":
                                                    t.text = (
                                                        token[: -len(enclitic)]
                                                        + "s"
                                                    )
                                                    t.startchar = start_char
                                                    t.endchar = (
                                                        start_char
                                                        + len(token)
                                                        - len(enclitic)
                                                    )
                                                    if mode == "index":
                                                        self._cache.append(
                                                            copy.deepcopy(t)
                                                        )
                                                    yield t
                                                    t.text = "ne"
                                                    t.startchar = (
                                                        start_char
                                                        + len(
                                                        token[
                                                        : -len(
                                                            enclitic
                                                        )
                                                        ]
                                                    )
                                                    )
                                                    t.endchar = (
                                                        start_char
                                                        + len(
                                                        token[
                                                        : -len(
                                                            enclitic
                                                        )
                                                        ]
                                                    )
                                                        + len(enclitic)
                                                    )
                                                    if mode == "index":
                                                        self._cache.append(
                                                            copy.deepcopy(t)
                                                        )
                                                    yield t
                                                elif enclitic == "st":
                                                    if token.endswith("ust"):
                                                        t.text = token[
                                                                 : -len(enclitic)
                                                                 ]
                                                        t.startchar = (
                                                            start_char
                                                        )
                                                        t.endchar = (
                                                            start_char
                                                            + len(
                                                            token[
                                                            : -len(
                                                                enclitic
                                                            )
                                                            ]
                                                        )
                                                            - len(enclitic)
                                                        )
                                                        if mode == "index":
                                                            self._cache.append(
                                                                copy.deepcopy(
                                                                    t
                                                                )
                                                            )
                                                        yield t
                                                        t.text = "est"
                                                        t.startchar = (
                                                            start_char
                                                            + len(
                                                            token[
                                                            : -len(
                                                                enclitic
                                                            )
                                                            ]
                                                        )
                                                        )
                                                        t.endchar = (
                                                            start_char
                                                            + len(
                                                            token[
                                                            : -len(
                                                                enclitic
                                                            )
                                                            ]
                                                        )
                                                            + len(enclitic)
                                                        )
                                                        if mode == "index":
                                                            self._cache.append(
                                                                copy.deepcopy(
                                                                    t
                                                                )
                                                            )
                                                        yield t
                                                    else:
                                                        t.text = token[
                                                                 : -len(enclitic)
                                                                 ]
                                                        t.startchar = (
                                                            start_char
                                                        )
                                                        t.endchar = (
                                                            start_char
                                                            + len(
                                                            token[
                                                            : -len(
                                                                enclitic
                                                            )
                                                            ]
                                                        )
                                                            - len(enclitic)
                                                        )
                                                        if mode == "index":
                                                            self._cache.append(
                                                                copy.deepcopy(
                                                                    t
                                                                )
                                                            )
                                                        yield t
                                                        t.text = "est"
                                                        t.startchar = (
                                                            start_char
                                                            + len(
                                                            token[
                                                            : -len(
                                                                enclitic
                                                            )
                                                            ]
                                                        )
                                                        )
                                                        t.endchar = (
                                                            start_char
                                                            + len(
                                                            token[
                                                            : -len(
                                                                enclitic
                                                            )
                                                            ]
                                                        )
                                                            + len(enclitic)
                                                        )
                                                        if mode == "index":
                                                            self._cache.append(
                                                                copy.deepcopy(
                                                                    t
                                                                )
                                                            )
                                                        yield t
                                                elif enclitic == "'s":
                                                    t.text = token + "s"
                                                    t.startchar = start_char
                                                    t.endchar = (
                                                        start_char + len(token)
                                                    )
                                                    if mode == "index":
                                                        self._cache.append(
                                                            copy.deepcopy(t)
                                                        )
                                                    yield t
                                                    t.text = "es"
                                                    t.startchar = (
                                                        start_char
                                                        + len(token)
                                                        + 1
                                                    )
                                                    t.endchar = (
                                                        start_char
                                                        + len(token)
                                                        + len(enclitic)
                                                    )
                                                    if mode == "index":
                                                        self._cache.append(
                                                            copy.deepcopy(t)
                                                        )
                                                    yield t
                                                else:
                                                    t.text = token[
                                                             : -len(enclitic)
                                                             ]
                                                    t.startchar = start_char
                                                    t.endchar = (
                                                        start_char
                                                        + len(
                                                        token[
                                                        : -len(
                                                            enclitic
                                                        )
                                                        ]
                                                    )
                                                    )
                                                    if mode == "index":
                                                        self._cache.append(
                                                            copy.deepcopy(t)
                                                        )
                                                    yield t
                                                    t.text = enclitic
                                                    t.startchar = (
                                                        start_char
                                                        + len(
                                                        token[
                                                        : -len(
                                                            enclitic
                                                        )
                                                        ]
                                                    )
                                                    )
                                                    t.endchar = (
                                                        start_char
                                                        + len(
                                                        token[
                                                        : -len(
                                                            enclitic
                                                        )
                                                        ]
                                                    )
                                                        + len(enclitic)
                                                    )
                                                    if mode == "index":
                                                        self._cache.append(
                                                            copy.deepcopy(t)
                                                        )
                                                    yield t
                                                is_enclitic = True
                                                break

                                        if not is_enclitic:
                                            original_len = len(token)
                                            if chars:
                                                t.startchar = start_char
                                                t.endchar = (
                                                    start_char + original_len
                                                )
                                            if self.cached:
                                                self._cache.append(
                                                    copy.copy(t)
                                                )
                                            yield t

                                        start_char += len(token)
