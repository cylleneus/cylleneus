import copy
import re
from itertools import chain

from greekwordnet import GreekWordNet
from greekwordnet.greekwordnet import relation_types
from multiwordnet.wordnet import WordNet

from cylleneus.engine.analysis.filters import Filter
from cylleneus.lang import iso_639
from cylleneus.lang.morpho import leipzig2wn


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

            GWN = GreekWordNet()

            for t in tokens:
                if t.mode == "index":
                    pos = t.morpho[0]

                    if pos in "nvar":
                        lemma = t.lemma
                        results = GWN.lemmas(lemma=lemma, pos=pos).get()

                        if results:
                            morphos = t.morpho.split()

                            for result in results:
                                annotations = []
                                for morpho in morphos:
                                    if result["morpho"]:
                                        morpho = morpho[:-2] + result["morpho"][-2:]
                                    if (
                                        morpho[5] == "p"
                                        and result["morpho"][5] == "d"
                                    ):
                                        morpho = morpho[:5] + "d" + morpho[6:]
                                    annotations.append(morpho)
                                t.morpho = f"{result['morpho']}::{result['uri']}:0>{' '.join(annotations)}"
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
                    elif "#" in text or text.startswith("="):
                        yield t
                    elif leipzig2wn(t.original) != "----------":
                        yield t
                    elif text.isnumeric():
                        yield t
                    else:
                        if hasattr(t, "reltype"):
                            keys = ["lemma", "uri", "morpho"]
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
                                    results = GWN.lemmas_by_uri(
                                        kwargs["uri"]
                                    ).relations
                                else:
                                    kwargs.pop("uri")
                                    results = GWN.lemmas(**kwargs).relations
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
                                    results = GWN.lemmas_by_uri(
                                        kwargs["uri"]
                                    ).synsets_relations
                                else:
                                    kwargs.pop("uri")
                                    results = GWN.lemmas(
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
                                    results = GWN.lemmas_by_uri(kwargs["uri"])
                                else:
                                    kwargs.pop("uri")
                                    results = GWN.lemmas(**kwargs)

                                if results:
                                    for result in results:
                                        t.text = f"{result['lemma']}:{result['uri']}={result['morpho']}"
                                        yield t
                                else:
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

            GWN = GreekWordNet()

            for t in tokens:
                if t.mode == "index":
                    text = t.text
                    if text:
                        keys = ["lemma", "uri", "morpho"]
                        kwargs = {
                            k: v
                            for k, v in zip(
                                keys,
                                re.search(
                                    r"(\w+)(?::([\w\d]+))?(?:=(.+))?", text
                                ).groups(),
                            )
                        }

                        if kwargs["uri"] is not None:
                            results = GWN.lemmas_by_uri(kwargs["uri"]).synsets
                        else:
                            kwargs.pop("uri")
                            results = GWN.lemmas(**kwargs).synsets
                        for result in results:
                            for synset in chain(
                                result["synsets"]["literal"],
                                result["synsets"]["metonymic"],
                                result["synsets"]["metaphoric"],
                            ):
                                t.code = " ".join(
                                    [
                                        semfield["code"]
                                        for semfield in synset["semfield"]
                                    ]
                                )  ## kludgy
                                t.text = f"{synset['pos']}#{synset['offset']}"
                                if self.cached:
                                    self._cache.append(copy.copy(t))
                                yield t
                        else:
                            t.code = ""
                            t.text = ""
                            if self.cached:
                                self._cache.append(copy.copy(t))
                            yield t
                    else:
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
                            result = GWN.synsets(pos, offset).relations
                            if t.reltype in result.keys():
                                for relation in result[t.reltype]:
                                    t.text = f"{relation['pos']}#{relation['offset']}"
                                    yield t
                        else:
                            yield t
                    else:
                        yield t
