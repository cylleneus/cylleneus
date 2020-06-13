import copy
from unicodedata import normalize

from cylleneus.corpus.grk.tlg import AUTHOR_TAB
from cylleneus.engine.analysis.acore import CylleneusToken
from cylleneus.engine.analysis.tokenizers import Tokenizer
from cylleneus.lang.grk.beta2unicode import beta2unicode
from .core import diorisis2wn


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
                t.text = normalize("NFKC", data)
                yield t
            else:
                self._cache = []
                self._docix = kwargs.get("docix", None)

                if tokenize:
                    titleStmt = data.find('.//teiHeader').find('fileDesc').find('titleStmt')
                    auth_code = f"tlg{titleStmt.find('tlgAuthor').text}"
                    work_code = f"tlg{titleStmt.find('tlgId').text}"

                    body = data.find('.//text').find('body')

                    divs = AUTHOR_TAB[auth_code]["works"][work_code]["meta"]

                    meta = {"meta": divs}
                    divv = divs.split("-")
                    for k in divv:
                        meta[k] = None

                    sect_sent = 0
                    sect_pos = 0
                    current_refs = None
                    pos = 0
                    for sentence in body.iter("sentence"):
                        refs = sentence.get("location")
                        if refs != current_refs:
                            current_refs = refs
                            sect_pos = 0
                            sect_sent = 0
                        sent_id = sentence.get("id")
                        sect_sent += 1

                        for i, ref in enumerate(refs.split(".")):
                            meta[divv[i]] = ref

                        for sent_pos, word in enumerate(sentence.iter("word")):
                            t.boost = 1.0

                            sect_pos += 1
                            pos += 1

                            lemma = word.find("lemma").get("entry", None)
                            t.lemma = normalize("NFKC", lemma)

                            meta["sent_id"] = sent_id
                            meta["sent_pos"] = word.get("id")
                            meta["sect_pos"] = str(sect_pos)
                            meta["sect_sent"] = str(sect_sent)
                            t.meta = copy.copy(meta)

                            beta = word.get("form").upper()
                            form = normalize("NFKC", beta2unicode(beta + "\n" if beta.endswith("S") else beta))
                            if (
                                t.lemma.istitle()
                            ):
                                form = form.title()
                            t.text = form

                            if keeporiginal:
                                t.original = beta
                            t.stopped = False
                            if positions:
                                t.pos = start_pos + pos

                            original_len = len(form)
                            if chars:
                                t.startchar = start_char
                                t.endchar = start_char + original_len
                            start_char += original_len

                            POS = word.find("lemma").get("POS", None)
                            analyses = [
                                analysis.get("morph", None)
                                for analysis in word.find("lemma").iter("analysis")
                            ]
                            morphos = []
                            for analysis in analyses:
                                morphos += diorisis2wn(POS, analysis)
                            t.morpho = " ".join(morphos)

                            if self.cached:
                                self._cache.append(copy.deepcopy(t))
                            yield t
                else:
                    body = data.find('.//text').find('body')

                    tokens = []
                    for sentence in body.iter("sentence"):
                        for word in sentence.iter("word"):
                            form = word.get("form")
                            if not form:
                                continue
                            else:
                                tokens.append(form)
                    t.original = t.text = " ".join(tokens)
                    t.boost = 1.0
                    if positions:
                        t.pos = start_pos
                    if chars:
                        t.startchar = start_char
                        t.endchar = start_char + len(t.original)
                    yield t
