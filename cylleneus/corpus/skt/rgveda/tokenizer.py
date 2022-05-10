import copy
import re

from cylleneus.engine.analysis.acore import CylleneusToken
from cylleneus.engine.analysis.tokenizers import Tokenizer
from cylleneus.lang.skt import slp2deva, iast2slp
from .core import lemma_id, parse_morpho, lemma_morpho


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
                        if line and line.startswith("# text_line"):
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

                    meta = {
                        "meta": value["meta"],
                        "merge_on": value["merge_on"],
                        "layer":              None,
                        "sent_id":            None,
                        "sent_pos":           None,
                    }
                    refs = value["meta"].split("-")
                    relations_heads = value["deprel"]

                    sent_id = 0
                    current_sent_id = None
                    for line in value["text"]:
                        line = line.strip()
                        if line:
                            if line.startswith("#"):
                                label, value = line.split("=", maxsplit=1)
                                label = label.strip('#').strip()
                                value = value.strip()
                                
                                if label == "sent_id":
                                    current_sent_id = value
                                    sent_id += 1
                                    
                                    for k, v in zip(
                                        refs, value.split("_")[1:]
                                        ):
                                        meta[k] = v 
                                elif label == "layer":
                                    meta[label] = value
                            else:
                                (
                                    ID,
                                    FORM,
                                    LEMMA,
                                    UPOS,
                                    XPOS,
                                    MORPHO,
                                    HEAD,
                                    DEPREL,
                                    DEPS,
                                    _,  #
                                    LEMMA_ID,
                                    _,  # annotator
                                    PUNCT,
                                    _,
                                    UNSANDHIED,
                                    SEM,
                                ) = line.split("\t")
                                t.pos = int(ID)
                                meta["sent_id"] = sent_id
                                meta["sent_pos"] = int(ID)

                                t.text = FORM
                                t.original = FORM
                                t.lemma = LEMMA
                                t.dcs_id = LEMMA_ID
                
                                if HEAD != "_" and int(HEAD) != 0:
                                    meta["head_pos"] = int(HEAD)
                                else:
                                    meta["head_pos"] = None
                                t.morphosyntax = None if DEPREL == "_" else DEPREL
                                t.morpho = None if MORPHO == "_" else parse_morpho(UPOS, MORPHO)
                                t.synset = None if SEM == "_" else SEM.split(":")[0]
                                
                                t.meta = meta
                                
                                t.startchar = start_char
                                t.endchar = start_char + len(t.original)

                                if HEAD == "_" or int(HEAD) == 0 or relations_heads[current_sent_id][int(ID)] is None:
                                    t.meta["head_lemma"] = None
                                    self._cache.append(copy.deepcopy(t))
                                    yield copy.deepcopy(t)
                                else:
                                    head_lemma, head_id, head_pos = relations_heads[current_sent_id][int(ID)]
                                    head_pos = {"NOUN": "n", "VERB": "v", "ADJ": "a", "ADV": "r"}[head_pos] if head_pos in ["NOUN", "VERB", "ADJ", "ADV"] else None
                                    if head_pos is not None:
                                        try:
                                            head_morphos = lemma_morpho[head_id]
                                        except KeyError:
                                            t.meta["head_lemma"] = None
                                            self._cache.append(copy.deepcopy(t))
                                            yield copy.deepcopy(t)
                                        else:
                                            for annotation in head_morphos.split():
                                                t.meta["head_lemma"] = f"{head_lemma}:{head_id}={annotation}"
                                                self._cache.append(copy.deepcopy(t))
                                                yield copy.deepcopy(t)               
                                    
                                start_char += len(t.original) + 1
