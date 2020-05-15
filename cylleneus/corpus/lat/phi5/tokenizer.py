import copy
import re
import string
from collections import deque

from cylleneus.engine.analysis.acore import CylleneusToken
from cylleneus.engine.analysis.tokenizers import Tokenizer
from cylleneus.lang.lat import (
    PunktLatinCharsVars,
    compound,
    enclitics,
    exceptions,
    jvmap,
    proper_names,
    replacements,
    roman_to_arabic,
)


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
        if kwargs.get("docix") == self._docix and self._cache:
            yield from self.cache
        else:
            t = CylleneusToken(
                positions, chars, removestops=removestops, mode=mode, **kwargs
            )

            if t.mode == "query":
                t.original = t.text = value.translate(jvmap)
                yield t
            else:
                if not tokenize:
                    t.original = t.text = value["text"]
                    t.boost = 1.0
                    if positions:
                        t.pos = start_pos
                    if chars:
                        t.startchar = start_char
                        t.endchar = start_char + len(value["text"])
                    yield t
                else:
                    self._cache = []
                    self._docix = kwargs.get("docix", None)

                    word_tokenizer = PunktLatinCharsVars()
                    stopchars = str.maketrans(
                        "",
                        "",
                        string.punctuation.replace("&", "").replace("^", "")
                        + "†“”—\n\ŕ",
                    )

                    divs = {
                        i: div.lower()
                        for i, div in enumerate(value["meta"].split("-"))
                    }

                    lines = iter(value["text"].split("\n"))
                    tpos = start_pos
                    xtitle = ytitle = ztitle = speaker = ""
                    buffer = deque()
                    for line in lines:

                        def parse_phi_line(_line):
                            result = []
                            nonlocal xtitle, ytitle, ztitle, speaker, buffer
                            try:
                                ref, text = _line.split("\t")
                            except ValueError:
                                result.append((None, None))
                            else:
                                v, w, x, y, z = ref.rstrip(".").split(".")
                                offset = 0
                                # d is a number, followed by -, t, a then possibly another number or . for a title
                                # d can be 'opinc' 'sedinc' 'dub', 'inc',
                                # c can be 'Summ'
                                if x == "t":
                                    xtitle = text.translate(stopchars).strip()
                                if y == "t":
                                    if z:
                                        ytitle = text.translate(
                                            stopchars
                                        ).strip()
                                    else:
                                        speaker = text.translate(
                                            stopchars
                                        ).strip()
                                    result.append((None, [text]))
                                elif z == "t":
                                    ztitle = text.translate(stopchars).strip()
                                    result.append((None, [text]))
                                elif "        {" in text:
                                    result.append((None, [text]))
                                else:
                                    temp_tokens = word_tokenizer.word_tokenize(
                                        text
                                    )
                                    if temp_tokens:
                                        if (
                                            temp_tokens[0]
                                                .replace("j", "i")
                                                .replace("v", "u")
                                            not in proper_names.proper_names
                                        ):
                                            temp_tokens[0] = temp_tokens[
                                                0
                                            ].lower()

                                        if (
                                            temp_tokens[-1].endswith(".")
                                            and temp_tokens[-1] != ". . ."
                                        ):
                                            final_word = temp_tokens[-1][:-1]
                                            del temp_tokens[-1]
                                            temp_tokens += [final_word, "."]

                                        if temp_tokens[-1].endswith("-"):
                                            buffer += list(
                                                parse_phi_line(next(lines))
                                            )
                                            new_ref, new_tokens = buffer.pop()
                                            merged_word = (
                                                "2&"
                                                + temp_tokens[-1][:-1]
                                                + new_tokens[0]
                                            )
                                            del temp_tokens[-1]
                                            temp_tokens += [merged_word]
                                            del new_tokens[0]
                                            if new_tokens:
                                                if (
                                                    new_tokens[0]
                                                    in string.punctuation
                                                ):
                                                    new_token = (
                                                        f"^1{new_tokens[0]}"
                                                    )
                                                    del new_tokens[0]
                                                    new_tokens.insert(
                                                        0, new_token
                                                    )
                                                buffer.appendleft(
                                                    (new_ref, new_tokens)
                                                )

                                        for ix, token in enumerate(
                                            temp_tokens
                                        ):
                                            if temp_tokens[ix] == ". . .":
                                                temp_tokens.insert(
                                                    ix + 1, "&1"
                                                )
                                            if "&" in token:
                                                ppp = compound.is_ppp(
                                                    re.sub(r"[&\d]", "", token)
                                                )
                                            else:
                                                ppp = compound.is_ppp(token)
                                            if ppp:
                                                if ix == len(temp_tokens) - 1:
                                                    if not buffer:
                                                        try:
                                                            buffer += list(
                                                                parse_phi_line(
                                                                    next(lines)
                                                                )
                                                            )
                                                        except StopIteration:
                                                            continue
                                                    if "&" in buffer[0][1][0]:
                                                        copula = compound.is_copula(
                                                            buffer[0][1][0][2:]
                                                        )
                                                    else:
                                                        copula = compound.is_copula(
                                                            buffer[0][1][0]
                                                        )
                                                else:
                                                    copula = compound.is_copula(
                                                        temp_tokens[ix + 1]
                                                    )

                                                if (
                                                    copula
                                                    and ppp[1] == copula[2]
                                                ):
                                                    (
                                                        tense,
                                                        mood,
                                                        number,
                                                        i,
                                                    ) = copula
                                                    if buffer:
                                                        token = f"{token} &2{compound.copula[tense][mood][number][i]}"
                                                    else:
                                                        token = f"{token} {compound.copula[tense][mood][number][i]}"
                                                    del temp_tokens[ix]
                                                    if buffer:
                                                        del buffer[0][1][0]
                                                    else:
                                                        del temp_tokens[ix]
                                                    temp_tokens.insert(
                                                        ix, token
                                                    )
                                                    if (
                                                        ix
                                                        != len(temp_tokens) - 1
                                                    ):
                                                        if (
                                                            temp_tokens[ix + 1]
                                                            in string.punctuation
                                                        ):
                                                            new_token = f"^1{temp_tokens[ix + 1]} "
                                                            del temp_tokens[
                                                                ix + 1
                                                                ]
                                                            temp_tokens.insert(
                                                                ix + 1,
                                                                new_token,
                                                            )
                                    if buffer:
                                        for i in range(len(buffer)):
                                            result.append(buffer.pop())
                                    result.append(
                                        ((v, w, x, y, z), temp_tokens)
                                    )
                            yield from result

                        result = list(parse_phi_line(line))
                        act = scene = None
                        for ref, tokens in reversed(result):
                            enjambed = False
                            if not ref and not tokens:
                                start_char += len(line) + 1
                                continue
                            elif not ref:
                                text = tokens[0].strip().strip("{}")
                                if re.match(
                                    r"[IVXLDMivxldm]+\.[IVXLDMivxldm]+", text
                                ):
                                    act, scene = text.split(".")
                                    act = str(roman_to_arabic(act))
                                    scene = str(roman_to_arabic(scene))
                                start_char += len(line.split("\t")[1]) + 1
                                continue
                            notoken = 0

                            skip = False
                            for line_pos, token in enumerate(tokens):
                                if token == "{" or token == "}":
                                    skip = not skip
                                    start_char += len(token)
                                    continue
                                if skip:
                                    speaker = token.replace("v", "u")
                                    start_char += len(token)
                                    continue

                                offset = 0
                                line_pos -= notoken

                                meta = {}
                                # extra['meta'] = value['meta'].lower()
                                # setattr(t, 'meta', value['meta'].lower())
                                for i in range(len(divs)):
                                    meta[divs[len(divs) - (i + 1)]] = ref[
                                        -(5 - (5 - (i + 1)))
                                    ].strip("t")
                                    # setattr(t, divs[len(divs) - (i + 1)], ref[-(5 - (5 - (i + 1)))].strip('t'))
                                    if xtitle:
                                        if len(divs) >= 3:
                                            meta[
                                                f"{divs[len(divs) - 3]}_title"
                                            ] = xtitle
                                            # setattr(t, f"{divs[len(divs)-3]}_title", xtitle)
                                    if ytitle:
                                        if len(divs) >= 2:
                                            meta[
                                                f"{divs[len(divs) - 2]}_title"
                                            ] = ytitle
                                            # setattr(t, f"{divs[len(divs)-2]}_title", ytitle)
                                    if ztitle:
                                        if len(divs) >= 1:
                                            meta[
                                                f"{divs[len(divs) - 1]}_title"
                                            ] = ztitle
                                            # setattr(t, f"{divs[len(divs)-1]}_title", ztitle)
                                if act:
                                    meta["act"] = act
                                if scene:
                                    meta["scene"] = scene
                                # if speaker:
                                #     t.speaker = speaker
                                t.boost = 1.0

                                pre = re.search(r"^\^(\d+?)", token)
                                if pre:
                                    start_char -= int(pre.group(1))
                                    token = re.sub(r"^\^\d+?", "", token)
                                pre = re.search(r"^&(\d+?)", token)
                                if pre:
                                    start_char += int(pre.group(1))
                                    token = re.sub(r"^&\d+?", "", token)
                                if keeporiginal:
                                    t.original = token
                                t.stopped = False
                                original_length = len(token)

                                ltoken = token.lstrip(string.punctuation)
                                ldiff = original_length - len(ltoken)
                                if ldiff != 0:
                                    token = ltoken
                                rtoken = token.rstrip(string.punctuation)
                                rdiff = len(token) - len(rtoken)
                                if rdiff != 0:
                                    token = rtoken
                                ntoken = token.translate(stopchars)
                                ndiff = len(token) - len(ntoken)
                                if ndiff:
                                    token = ntoken
                                if not re.match(
                                    r"(?:[\d]&)?[\w]+\s(?:&[\d])?[\w]+", token
                                ):
                                    token = token.replace(" ", "")
                                if not token:
                                    start_char += original_length
                                    notoken += 1
                                    continue
                                else:
                                    if positions:
                                        meta["line_pos"] = line_pos
                                        t.pos = tpos
                                    t.meta = meta

                                    if (
                                        token not in exceptions
                                        and token.lower() not in exceptions
                                        and re.sub(r"\d&|&\d", "", token)
                                        not in exceptions
                                    ):
                                        if token in replacements:  # t.original
                                            for subtoken in replacements[
                                                token
                                            ]:
                                                t.text = subtoken.lower()
                                                t.startchar = start_char
                                                t.endchar = (
                                                    start_char
                                                    + original_length
                                                )
                                                if mode == "index":
                                                    if self.cached:
                                                        self._cache.append(
                                                            copy.copy(t)
                                                        )
                                                yield t
                                            start_char += original_length
                                            tpos += 1
                                            continue

                                        if re.match(
                                            r"(?:[\d]&)?[\w]+\s(?:&[\d])?[\w]+",
                                            token,
                                        ):
                                            ppp, copula = token.split(" ")
                                            post = re.match(
                                                r"([\d])&[\w]+", ppp
                                            )
                                            if post:
                                                offset += int(post.group(1))
                                                ppp = re.sub(r"[\d]&", "", ppp)
                                                original_length -= 2
                                                enjambed = True
                                            t.text = ppp.lower()
                                            t.startchar = start_char
                                            t.endchar = (
                                                start_char + len(ppp) + offset
                                            )
                                            if mode == "index":
                                                if self.cached:
                                                    self._cache.append(
                                                        copy.copy(t)
                                                    )
                                            yield t
                                            pre = re.search(r"&(\d+?)", copula)
                                            if pre:
                                                start_char += int(pre.group(1))
                                                copula = re.sub(
                                                    r"&\d+?", "", copula
                                                )
                                                original_length -= 2
                                                enjambed = True
                                            t.text = copula.lower()
                                            t.startchar = (
                                                start_char + len(ppp) + 1
                                            )
                                            t.endchar = (
                                                start_char
                                                + len(ppp)
                                                + 1
                                                + len(copula)
                                            )
                                            if mode == "index":
                                                if self.cached:
                                                    self._cache.append(
                                                        copy.copy(t)
                                                    )
                                            yield t
                                            start_char += original_length
                                            tpos += 1
                                            continue
                                        else:
                                            post = re.match(
                                                r"([\d])&[\w]+", token
                                            )
                                            if post:
                                                offset += int(post.group(1))
                                                token = re.sub(
                                                    r"[\d]&", "", token
                                                )
                                                original_length -= 2
                                                enjambed = True
                                            else:
                                                offset = 0

                                        is_enclitic = False
                                        for enclitic in enclitics:
                                            if token.lower().endswith(
                                                enclitic
                                            ):
                                                is_enclitic = True
                                                if enclitic == "ne":
                                                    t.text = (
                                                        token[: -len(enclitic)]
                                                    ).lower()
                                                    t.startchar = start_char
                                                    t.endchar = start_char + (
                                                        len(token)
                                                        - len(enclitic)
                                                    )
                                                    if mode == "index":
                                                        if self.cached:
                                                            self._cache.append(
                                                                copy.copy(t)
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
                                                        + offset
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
                                                        + offset
                                                    )
                                                    if mode == "index":
                                                        if self.cached:
                                                            self._cache.append(
                                                                copy.copy(t)
                                                            )
                                                    yield t
                                                elif enclitic == "n":
                                                    t.text = (
                                                        token[: -len(enclitic)]
                                                        + "s"
                                                    ).lower()
                                                    t.startchar = start_char
                                                    t.endchar = (
                                                        start_char
                                                        + (len(token) + 1)
                                                        - len(enclitic)
                                                    )
                                                    if mode == "index":
                                                        if self.cached:
                                                            self._cache.append(
                                                                copy.copy(t)
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
                                                        + offset
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
                                                        + offset
                                                    )
                                                    if mode == "index":
                                                        if self.cached:
                                                            self._cache.append(
                                                                copy.copy(t)
                                                            )
                                                    yield t
                                                elif enclitic == "st":
                                                    if token.endswith("ust"):
                                                        t.text = (
                                                            token[
                                                            : -len(
                                                                enclitic
                                                            )
                                                              + 1
                                                            ]
                                                        ).lower()
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
                                                              + 1
                                                            ]
                                                        )
                                                            - len(enclitic)
                                                        )
                                                        if mode == "index":
                                                            if self.cached:
                                                                self._cache.append(
                                                                    copy.copy(
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
                                                              + 1
                                                            ]
                                                        )
                                                            + offset
                                                        )
                                                        t.endchar = (
                                                            start_char
                                                            + len(
                                                            token[
                                                            : -len(
                                                                enclitic
                                                            )
                                                              + 1
                                                            ]
                                                        )
                                                            + len(enclitic)
                                                            + offset
                                                        )
                                                        if mode == "index":
                                                            if self.cached:
                                                                self._cache.append(
                                                                    copy.copy(
                                                                        t
                                                                    )
                                                                )
                                                        yield t
                                                    else:
                                                        t.text = (
                                                            token[
                                                            : -len(
                                                                enclitic
                                                            )
                                                            ]
                                                        ).lower()
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
                                                            if self.cached:
                                                                self._cache.append(
                                                                    copy.copy(
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
                                                            + offset
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
                                                            + offset
                                                        )
                                                        if mode == "index":
                                                            if self.cached:
                                                                self._cache.append(
                                                                    copy.copy(
                                                                        t
                                                                    )
                                                                )
                                                        yield t
                                                elif enclitic == "'s":
                                                    t.text = (
                                                        token.lower() + "s"
                                                    )
                                                    t.startchar = start_char
                                                    t.endchar = (
                                                        start_char + len(token)
                                                    )
                                                    if mode == "index":
                                                        if self.cached:
                                                            self._cache.append(
                                                                copy.copy(t)
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
                                                        if self.cached:
                                                            self._cache.append(
                                                                copy.copy(t)
                                                            )
                                                    yield t
                                                else:
                                                    t.text = (
                                                        token[: -len(enclitic)]
                                                    ).lower()
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
                                                        if self.cached:
                                                            self._cache.append(
                                                                copy.copy(t)
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
                                                        + offset
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
                                                        + offset
                                                    )
                                                    if mode == "index":
                                                        if self.cached:
                                                            self._cache.append(
                                                                copy.copy(t)
                                                            )
                                                    yield t
                                                break
                                    else:
                                        is_enclitic = False
                                        post = re.match(r"([\d])&[\w]+", token)
                                        if post:
                                            offset += int(post.group(1))
                                            token = re.sub(r"[\d]&", "", token)
                                            original_length -= 2
                                            enjambed = True
                                    if not is_enclitic:
                                        t.text = token
                                        if chars:
                                            t.startchar = start_char + ldiff
                                            t.endchar = (
                                                start_char
                                                + original_length
                                                - rdiff
                                                + offset
                                            )
                                        if mode == "index":
                                            if self.cached:
                                                self._cache.append(
                                                    copy.copy(t)
                                                )
                                        yield t
                                        tpos += 1
                                    if enjambed:
                                        start_char += original_length + offset
                                    else:
                                        start_char += original_length
                            start_char += 1  # \n
