import copy
import re

from cylleneus.corpus.lat.perseus import mapping
from cylleneus.engine.analysis.filters import Filter
from cylleneus.lang.morpho import leipzig2wn
from latinwordnet import LatinWordNet
from latinwordnet.latinwordnet import relation_types
from .core import relations


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

            LWN = LatinWordNet()

            jvmap = str.maketrans("jv", "iu", "")
            for t in tokens:
                if t.mode == "index":
                    morpho = t.morpho
                    lemma = t.lemma
                    if morpho[0] in "nvar":
                        if "#" in lemma:
                            kwargs = mapping[lemma.replace("#", "")]
                        else:
                            kwargs = None

                        if kwargs:
                            results = LWN.lemmas_by_uri(kwargs["uri"]).get()
                        else:
                            results = LWN.lemmas(lemma, morpho[0]).get()
                        if results:
                            for result in results:
                                morpho = morpho[:-2] + result["morpho"][-2:]
                                if (
                                    morpho[5] == "p"
                                    and result["morpho"][5] == "d"
                                ):
                                    morpho = morpho[:5] + "d" + morpho[6:]
                                t.morpho = f"{result['morpho']}::{result['uri']}:0>{morpho}"
                                t.text = (
                                    f"{result['lemma']}:"
                                    f"{result['uri']}={result['morpho']}"
                                )
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
                    elif "#" in text:
                        yield t
                    elif leipzig2wn(t.original) != "----------":
                        yield t
                    elif text.isnumeric():
                        yield t
                    else:
                        if hasattr(t, "reltype"):
                            if t.reltype in ["\\", "/", "+c", "-c"]:
                                keys = ["lemma", "uri", "morpho"]
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
                                    results = LWN.lemmas_by_uri(
                                        kwargs["uri"]
                                    ).relations
                                else:
                                    kwargs.pop("uri")
                                    results = LWN.lemmas(**kwargs).relations
                            else:
                                keys = ["lemma", "uri", "morpho"]
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
                                    results = LWN.lemmas_by_uri(
                                        kwargs["uri"]
                                    ).synsets_relations
                                else:
                                    kwargs.pop("uri")
                                    results = LWN.lemmas(
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
                                            t.text = f"{relation['lemma']}:{relation['uri']}={relation['morpho']}"
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
                                keys = ["lemma", "uri", "morpho"]
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
                                    results = LWN.lemmas_by_uri(kwargs["uri"])
                                else:
                                    kwargs.pop("uri")
                                    results = LWN.lemmas(**kwargs)

                                if results:
                                    for result in results:
                                        t.text = f"{result['lemma']}:{result['uri']}={result['morpho']}"
                                        yield t
                                else:
                                    yield t


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
                relation = t.morphosyntax
                if relation:
                    t.text = relation
                    yield t
            elif t.mode == "query":
                text = t.original
                if text:
                    t.text = relations[text]
                    yield t
