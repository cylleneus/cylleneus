import copy

from cylleneus.engine.analysis.tokenizers import Tokenizer
from cylleneus.engine.analysis.acore import CylleneusToken


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
        keeporiginal=False,
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
                t.text = data
                yield t
            else:
                self._cache = []
                self._docix = kwargs.get("docix", None)

                if not tokenize:
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
                else:
                    divs = data["meta"].split('-')
                    meta = {"meta": data["meta"].lower()}
                    meta['sect_sent'] = None
                    meta['sect_pos'] = None
                    meta['sent_id'] = 0  # id
                    meta['sent_pos'] = 0  # id

                    t.figure = t.source = t.target = None
                    t.startchar = start_char
                    t.endchar = start_char

                    for el in data["text"].find("body").iter():
                        if el.tag == "position":
                            refs = el.text.split(',')
                            for i, div in enumerate(divs):
                                meta[div] = refs[i]
                        elif el.tag == "word":
                            t.text = el.get("freeText")
                            analysis = el.find("analysis")
                            t.lemma = analysis.get("lemmaId") if analysis is not None else ""
                            inflexion = analysis.find("inflexion") if analysis is not None else None
                            t.morpho = inflexion.get("iid") if inflexion is not None else ""

                            meta["sent_id"] = el.get("id")
                            meta["sent_pos"] = el.get("id")
                            t.meta = copy.copy(meta)
                            # t.morphosyntax = None  # where does CONN, PREP etc come from?
                            t.boost = 1.0
                            t.stopped = False
                            if positions:
                                t.pos = int(meta["sent_id"])

                            group = el.getnext()

                            while group is not None and group.tag == "group":
                                subtype = group.get("subType")
                                if subtype == "Metonym":
                                    t.figure = "~"
                                elif subtype == "MetaphorRelatedWord" or subtype == "Personification" or subtype == \
                                    "SetExpression":
                                    t.figure = "#"
                                elif subtype == "Metaphtonymy":
                                    pass
                                elif subtype == "ConceptualGroup":
                                    if t.figure == "~":
                                        t.source = group.find("attribute[@name='Domain1']").get("value")
                                        t.target = group.find("attribute[@name='Domain2']").get("value")
                                    elif t.figure == "#":
                                        t.source = group.find("attribute[@name='SourceDomain']").get("value")
                                        t.target = group.find("attribute[@name='TargetDomain']").get("value")
                                elif subtype == "ConceptualGroup2":
                                    if t.figure == "~":
                                        # only the final metonymy in the hierarchy
                                        t.source = group.find("attribute[@name='Domain2o1']").get("value")
                                        t.target = group.find("attribute[@name='Domain2o2']").get("value")
                                    elif t.figure == "#":
                                        t.source = group.find("attribute[@name='SourceDomain']").get("value")
                                        t.target = group.find("attribute[@name='TargetDomain']").get("value")
                                    elif t.figure == "@":  # metaphtonymy
                                        pass
                                group = group.getnext()

                            if self.cached:
                                self._cache.append(copy.copy(t))

                            if chars:
                                t.startchar = start_char
                                t.endchar = start_char + len(t.text)
                                start_char = t.endchar + 1

                            yield t

                            t.figure = t.source = t.target = None
