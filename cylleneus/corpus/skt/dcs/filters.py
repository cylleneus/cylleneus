import copy
import re

from multiwordnet.wordnet import WordNet
from sanskritwordnet import SanskritWordNet, relation_types

from cylleneus.engine.analysis.filters import Filter
from cylleneus.lang import iso_639
from cylleneus.lang.morpho import Morph, leipzig2wn
# from cylleneus.lang.skt import iast2slp, slp2deva
from .core import (lemma_id, lemma_morpho, pos_mapping, wn_mappings, xpos_mapping)

SWN = SanskritWordNet()


class MorphosyntaxFilter(Filter):
    is_morph = True

    def __init__(self, **kwargs):
        super(MorphosyntaxFilter, self).__init__()
        self.__dict__.update(**kwargs)

    def __eq__(self, other):
        return (
            other
            and self.__class__ is other.__class__
            and self.__dict__ == other.__dict__
        )

    def __ne__(self, other):
        return not self == other

    def __call__(self, tokens, **kwargs):
        for t in tokens:
            if t.mode == "index":
                text = t.morphosyntax.strip()
                if text:
                    t.text = text
                    yield t
            elif t.mode == "query":
                text = t.original
                if text:
                    if text in xpos_mapping:
                        t.text = text
                        yield t
                    else:
                        if text in pos_mapping:
                            t.text = pos_mapping[text]
                            yield t


class CachedLemmaFilter(Filter):
    is_morph = True

    def __init__(self, cached=True, **kwargs):
        super(CachedLemmaFilter, self).__init__()
        self.cached = cached
        self._cache = None
        self._docix = None
        self.__dict__.update(**kwargs)

    @property
    def cache(self):
        return copy.deepcopy(self._cache)

    def __eq__(self, other):
        return (
            other
            and self.__class__ is other.__class__
            and self.__dict__ == other.__dict__
        )

    def __ne__(self, other):
        return not self == other

    def __call__(self, tokens, **kwargs):
        if kwargs.get("docix", None) == self._docix and self._cache:
            yield from self.cache
        else:
            self._cache = []
            self._docix = kwargs.get("docix", None)

            for t in tokens:
                if t.mode == "index":
                    if t.lemma:
                        lemma = t.lemma
                        dcs_id = t.dcs_id if t.dcs_id else None
                        try:
                            morphos = lemma_morpho[dcs_id]
                        except KeyError:
                            continue

                        annotation = t.morpho if t.morpho is not None else None
                        for i, morpho in enumerate(morphos.split()):
                            uri = lemma_id[lemma][morpho]
                            if annotation is not None:
                                annotations = [
                                    annotation,
                                ]
                                for desc in annotations:
                                    annotation = str(
                                        Morph(morpho) + Morph(desc)
                                    )
                                    t.morpho = (
                                        f"{morpho}::{uri}:{i}>{annotation}"
                                    )
                                    t.text = f"{lemma}:{uri}={morpho}"
                                    if self.cached:
                                        self._cache.append(copy.copy(t))
                                    yield t

                                    # # Emit Devanagari
                                    # t.text = f"{slp2deva(iast2slp(lemma))}:{uri}={morpho}"
                                    # t.mode = "skip"
                                    # yield t

                            else:
                                t.morpho = f"{morpho}::{uri}:{i}>{morpho}"
                                t.text = f"{lemma}:{uri}={morpho}"
                                if self.cached:
                                    self._cache.append(copy.copy(t))
                                yield t
                elif t.mode == "query":
                    # Lexical relation
                    if "::" in t.text:
                        reltype, query = t.text.split("::")
                        t.reltype = reltype
                        t.text = query

                    text = t.text
                    if "?" in text:
                        language, word = text.split("?")
                        t.language = language
                        t.text = word
                        yield t
                    elif "#" in text or text.startswith("="):
                        yield t
                    elif leipzig2wn(t.original) != "----------":
                        yield t
                    elif text.isnumeric():
                        yield t
                    else:
                        if hasattr(t, "reltype"):
                            keys = ["transliteration", "uri", "morpho"]
                            if t.reltype in ["\\", "/", "+c", "-c"]:
                                kwargs = {
                                    k: v
                                    for k, v in zip(
                                        keys,
                                        re.search(
                                            r"(\w+)(?::([A-z0-9]+))?(?:=(.+))?",
                                            text,
                                        ).groups(),
                                    )
                                }
                                if kwargs["uri"] is not None:
                                    results = SWN.lemmas_by_uri(
                                        kwargs["uri"]
                                    ).relations
                                else:
                                    kwargs.pop("uri")
                                    results = SWN.lemmas(**kwargs).relations
                            else:
                                kwargs = {
                                    k: v
                                    for k, v in zip(
                                        keys,
                                        re.search(
                                            r"(\w+)(?::([A-z0-9]+))?(?:=(.+))?",
                                            text,
                                        ).groups(),
                                    )
                                }
                                if kwargs["uri"] is not None:
                                    results = SWN.lemmas_by_uri(
                                        kwargs["uri"]
                                    ).synsets_relations
                                else:
                                    kwargs.pop("uri")
                                    results = SWN.lemmas(
                                        **kwargs
                                    ).synsets_relations
                            if results:
                                for result in results:
                                    if (
                                        relation_types[t.reltype]
                                        in result["relations"].keys()
                                    ):
                                        for relation in result["relations"][
                                            relation_types[t.reltype]
                                        ]:
                                            t.text = (
                                                f"{relation['transliteration']}:{relation['uri']}"
                                                f"={relation['morpho']}"
                                            )
                                            yield t
                        else:
                            # query may be provided as lemma:uri=morpho
                            if all(
                                re.match(
                                    r"(\w+)(?::([A-z0-9]+))?(?:=(.+))?", text
                                ).groups()
                            ):
                                t.text = text
                                yield t
                            else:
                                keys = ["transliteration", "uri", "morpho"]
                                kwargs = {
                                    k: v
                                    for k, v in zip(
                                        keys,
                                        re.search(
                                            r"(\w+)(?::([A-z0-9]+))?(?:=(.+))?",
                                            text,
                                        ).groups(),
                                    )
                                }
                                if kwargs["uri"] is not None:
                                    results = SWN.lemmas_by_uri(kwargs["uri"])
                                else:
                                    kwargs.pop("uri")
                                    results = SWN.lemmas(**kwargs)

                                if results:
                                    for result in results:
                                        if result["uri"] is not None:
                                            t.text = f"{result['transliteration']}:{result['uri']}={result['morpho']}"
                                            yield t


class CachedSynsetFilter(Filter):
    is_morph = True

    def __init__(self, cached=True, **kwargs):
        super(CachedSynsetFilter, self).__init__()
        self._cache = None
        self._docix = None
        self.cached = cached
        self.__dict__.update(**kwargs)

    @property
    def cache(self):
        return copy.deepcopy(self._cache)

    def __eq__(self, other):
        return (
            other
            and self.__class__ is other.__class__
            and self.__dict__ == other.__dict__
        )

    def __ne__(self, other):
        return not self == other

    def __call__(self, tokens, **kwargs):
        if kwargs.get("docix", None) == self._docix and self._cache:
            yield from self.cache
        else:
            self._cache = []
            self._docix = kwargs.get("docix", None)

            for t in tokens:
                if t.mode == "index":
                    sem = t.synset
                    if sem:
                        synset_id = wn_mappings.get(sem, None)

                        if synset_id:
                            t.text = synset_id
                            if self.cached:
                                self._cache.append(copy.copy(t))
                            yield t
                elif t.mode == "query":
                    if hasattr(t, "language"):
                        language = t.language
                        text = t.text

                        if hasattr(t, "reltype"):
                            for lemma in WordNet(iso_639[language]).get(text):
                                if t.reltype in ["\\", "/", "+c", "-c"]:
                                    lexical = True
                                else:
                                    lexical = False
                                for relation in WordNet(
                                    iso_639[language]
                                ).get_relations(
                                    w_source=lemma,
                                    type=t.reltype,
                                    lexical=lexical,
                                ):
                                    if relation.is_lexical:
                                        for (
                                            synset
                                        ) in relation.w_target.synsets:
                                            t.text = synset.id
                                            yield t
                                    else:
                                        t.text = relation.id_target
                                        yield t
                        else:
                            for lemma in WordNet(iso_639[language]).get(text):
                                for synset in lemma.synsets:
                                    t.text = synset.id
                                    yield t
                    elif "#" in t.text:  # raw synset
                        if hasattr(t, "reltype"):
                            pos, offset = t.text.split("#")
                            result = SWN.synsets(pos, offset).relations
                            if t.reltype in result.keys():
                                for relation in result[t.reltype]:
                                    t.text = f"{relation['pos']}#{relation['offset']}"
                                    yield t
                        else:
                            yield t
                    elif t.text.startswith("="):
                        q = t.text[1:]
                        synsets = SWN.synsets(gloss=q).search()
                        for synset in synsets:
                            t.text = f"{synset['pos']}#{synset['offset']}"
                            yield t
                    else:
                        yield t


class SemfieldFilter(Filter):
    is_morph = True

    def __init__(self, **kwargs):
        super(SemfieldFilter, self).__init__()
        self.__dict__.update(**kwargs)

    def __eq__(self, other):
        return (
            other
            and self.__class__ is other.__class__
            and self.__dict__ == other.__dict__
        )

    def __ne__(self, other):
        return not self == other

    def __call__(self, tokens, **kwargs):
        for t in tokens:
            if t.mode == "index":
                synset_id = t.text
                pos, offset = synset_id.split("#")
                synsets = SWN.synsets(pos=pos, offset=offset).get()
                if synsets:
                    for synset in synsets:
                        codes = [
                            semfield["code"]
                            for semfield in synset["semfield"]
                        ]
                        for code in codes:
                            t.text = code
                            yield t
            elif t.mode == "query":
                text = t.original
                if text:
                    if text.isnumeric():
                        results = SWN.semfields(code=text)
                    else:
                        results = SWN.semfields(english=text).search()
                    if results:
                        for result in results:
                            t.text = result["code"]
                            yield t
                else:
                    yield t
