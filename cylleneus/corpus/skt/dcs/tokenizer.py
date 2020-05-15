import copy
import re

from cylleneus.engine.analysis.acore import CylleneusToken
from cylleneus.engine.analysis.tokenizers import Tokenizer
from cylleneus.lang.skt import slp2deva, iast2slp

from .core import parse_morpho


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
        value,
        positions=False,
        chars=False,
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
                t.text = t.original = value
                yield t
            else:
                if not tokenize:
                    lines = []
                    for line in value["text"]:
                        line = re.sub(r"\t+", "\t", line.strip())
                        if line:
                            if line.startswith("# text_line"):
                                text = line.split("# text_line: ")[1]
                                lines.append(text)
                    t.original = t.text = "\n".join([line for line in lines])
                    t.boost = 1.0
                    if positions:
                        t.pos = start_pos
                    if chars:
                        t.startchar = start_char
                        t.endchar = start_char + len(t.text)
                    yield t
                else:
                    self._cache = []
                    self._docix = kwargs.get("docix", None)

                    t.boost = 1.0
                    t.pos = t.startchar = t.endchar = 0

                    _meta = {
                        "text":                 None,  # work title
                        "text_id":              None,
                        "chapter":              None,  # reference
                        "chapter_id":           None,
                        "text_line":            None,  # the text
                        "text_line_id":         None,
                        "text_line_counter":    None,  # line number
                        "text_line_subcounter": None,  # token number
                    }

                    sect_pos = 0
                    sent_pos = 0
                    for line in value["text"]:
                        line = line.strip()
                        if line:
                            if line.startswith("#"):
                                try:
                                    label, value = line.split(":", maxsplit=1)
                                except ValueError:
                                    continue
                                label = label.split(" ", maxsplit=1)[1].strip()
                                value = value.strip()
                                _meta[label] = (
                                    value
                                    if not value.isnumeric()
                                    else int(value)
                                )

                                if label == "text_line_counter":
                                    sent_pos = 0
                                elif label == "text_line_subcounter":
                                    sent_pos = 0
                            else:
                                try:
                                    (
                                        ID,
                                        FORM,
                                        LEMMA,
                                        UPOS,
                                        XPOS,
                                        MORPHO,
                                        _,
                                        _,
                                        _,
                                        _,
                                        LEMMA_ID,
                                        PADA,
                                        SEM,
                                    ) = line.split("\t")
                                except ValueError:
                                    try:
                                        (
                                            ID,
                                            FORM,
                                            LEMMA,
                                            _,
                                            XPOS,
                                            _,
                                            _,
                                            _,
                                            _,
                                            LEMMA_ID,
                                            _,
                                            _,
                                        ) = line.split("\t")
                                    except ValueError:
                                        try:
                                            (
                                                ID,
                                                FORM,
                                                _,
                                                _,
                                                _,
                                                _,
                                                _,
                                                _,
                                                _,
                                                _,
                                            ) = line.split("\t")
                                        except ValueError:
                                            continue
                                        else:
                                            t.original = FORM
                                            sect_pos += 1
                                            sent_pos += 1
                                            t.pos = sent_pos
                                            continue
                                    else:
                                        # t.mode = "index"

                                        if FORM == "_":
                                            t.text = t.original
                                        else:
                                            sect_pos += 1
                                            sent_pos += 1

                                            t.text = FORM
                                            t.original = FORM
                                            t.pos = sent_pos
                                        t.lemma = LEMMA
                                        t.dcs_id = LEMMA_ID
                                        t.morphosyntax = XPOS
                                        t.morpho = None

                                        t.meta = {
                                            "meta":      "chapter-line",
                                            "chapter":   _meta["chapter"],
                                            "line":      _meta["text_line_counter"],
                                            "sect_pos":  sect_pos,
                                            "sect_sent": _meta[
                                                             "text_line_counter"
                                                         ],
                                            "sent_id":   _meta["text_line_id"],
                                            "sent_pos":  sent_pos,
                                        }
                                        t.startchar = start_char
                                        t.endchar = start_char + len(
                                            t.original
                                        )
                                        yield t

                                        # # Emit Devanagari
                                        # t.text = slp2deva(iast2slp(t.text))
                                        # t.mode = "skip"
                                        # yield t

                                        start_char += len(t.original) + 1
                                else:
                                    # t.mode = "index"

                                    if FORM == "_":
                                        t.text = t.original
                                    else:
                                        sect_pos += 1
                                        sent_pos += 1

                                        t.text = FORM
                                        t.original = FORM
                                        t.pos = sent_pos
                                    t.lemma = LEMMA
                                    t.dcs_id = LEMMA_ID
                                    t.morphosyntax = XPOS
                                    if MORPHO == "_" or not MORPHO:
                                        t.morpho = None
                                    else:
                                        t.morpho = parse_morpho(XPOS, MORPHO)
                                    t.meta = {
                                        "meta":      "chapter-line",
                                        "chapter":   _meta["chapter"],
                                        "line":      _meta["text_line_counter"],
                                        "sect_pos":  sect_pos,
                                        "sect_sent": _meta[
                                                         "text_line_counter"
                                                     ],
                                        "sent_id":   _meta["text_line_id"],
                                        "sent_pos":  sent_pos,
                                    }
                                    t.startchar = start_char
                                    t.endchar = start_char + len(t.original)
                                    yield t

                                    # # Emit Devanagari
                                    # t.text = slp2deva(iast2slp(t.text))
                                    # t.mode = "skip"
                                    # yield t

                                    start_char += len(t.original) + 1
