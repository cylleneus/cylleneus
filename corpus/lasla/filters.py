import copy
import re

from engine.analysis.filters import Filter
from lang.latin.morphology import leipzig2wn
from latinwordnet import LatinWordNet
from latinwordnet.latinwordnet import relation_types
from .core import bpn2wn, mapping, subord, subord_codes


class MorphosyntaxFilter(Filter):
    is_morph = True

    def __init__(self, **kwargs):
        super(MorphosyntaxFilter, self).__init__()
        self.__dict__.update(**kwargs)

    def __eq__(self, other):
        return (other
                and self.__class__ is other.__class__
                and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self == other

    def __call__(self, tokens, **kwargs):
        for t in tokens:
            if t.mode == 'index':
                text = t.morphosyntax.strip()
                if text:
                    t.text = text
                    yield t
            elif t.mode == 'query':
                text = t.text
                if text:
                    if text.startswith('?'):
                        text = text[1:].replace('u', 'v').upper()
                        if text in subord:
                            for code in subord[text]:
                                t.text = code
                                yield t
                    else:
                        if text in subord_codes:
                            t.text = text
                            yield t
                        else:
                            if text in subord:
                                for code in subord[text]:
                                    t.text = code
                                    yield t


class CachedLemmaFilter(Filter):
    is_morph = True

    def __init__(self, **kwargs):
        super(CachedLemmaFilter, self).__init__()
        self.__dict__.update(**kwargs)
        self._cache = None
        self._docix = None

    @property
    def cache(self):
        return copy.deepcopy(self._cache)

    def __eq__(self, other):
        return (other
                and self.__class__ is other.__class__
                and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self == other

    def __call__(self, tokens, **kwargs):
        if kwargs.get('docix', None) == self._docix and self._cache:
            yield from self.cache
        else:
            self._cache = []
            self._docix = kwargs.get('docix', None)

            LWN = LatinWordNet()

            jvmap = str.maketrans('jv', 'iu', '')
            for t in tokens:
                if t.mode == 'index':
                    if t.lemma:
                        lemma = t.lemma
                        ix = t.lemma_n if t.lemma_n.strip() else '-'
                        morphos = mapping[lemma][ix]['morpho']
                        uris = mapping[lemma][ix]['uri']

                        if t.morpho is not None:
                            annotation = bpn2wn(t.morpho)
                        else:
                            annotation = None
                        lemma = lemma.lower().strip('_').translate(jvmap)

                        for uri in uris:
                            for i, morpho in enumerate(morphos):
                                if annotation is not None:
                                    if '/' in annotation:  # n-s---m/nn3-
                                        head, *alts, tail = re.search(
                                            r'^(.*?)([a-z1-9\-])/([a-z1-9\-])(.*?)$', annotation).groups()
                                        annotations = [f"{head}{alt}{tail}" for alt in alts]
                                    else:
                                        annotations = [annotation,]
                                    for annotation in annotations:
                                        t.morpho = f"{morpho}::{uri}:{i}>{annotation}"
                                        t.text = f"{lemma}:{uri}={morpho}"
                                        self._cache.append(copy.copy(t))
                                        yield t
                                else:
                                    t.morpho = f"{morpho}::{uri}:{i}>{morpho}"
                                    t.text = f"{lemma}:{uri}={morpho}"
                                    self._cache.append(copy.copy(t))
                                    yield t
                elif t.mode == 'query':
                    # Lexical relation
                    if '::' in t.text:
                        reltype, query = t.text.split('::')
                        t.reltype = reltype
                        t.text = query

                    text = t.text
                    if '?' in text:
                        language, word = text.split('?')
                        t.language = language
                        t.text = word
                        yield t
                    elif '#' in text:
                        yield t
                    elif leipzig2wn(t.original) != '----------':
                        yield t
                    elif text.isnumeric():
                        yield t
                    else:
                        if hasattr(t, 'reltype'):
                            if t.reltype in ['\\', '/', '+c', '-c']:
                                keys = ['lemma', 'uri', 'morpho']
                                kwargs = {
                                    k: v
                                    for k, v in zip(
                                        keys,
                                        re.search(r"(\w+)(?::([A-z0-9]+))?(?:=(.+))?", text).groups()
                                    )
                                }
                                if kwargs['uri'] is not None:
                                    results = LWN.lemmas_by_uri(kwargs['uri']).relations
                                else:
                                    kwargs.pop('uri')
                                    results = LWN.lemmas(**kwargs).relations
                            else:
                                keys = ['lemma', 'uri', 'morpho']
                                kwargs = {
                                    k: v
                                    for k, v in zip(
                                        keys,
                                        re.search(r"(\w+)(?::([A-z0-9]+))?(?:=(.+))?", text).groups()
                                    )
                                }
                                if kwargs['uri'] is not None:
                                    results = LWN.lemmas_by_uri(kwargs['uri']).synsets_relations
                                else:
                                    kwargs.pop('uri')
                                    results = LWN.lemmas(**kwargs).synsets_relations
                            if results:
                                for result in results:
                                    if relation_types[t.reltype] in result['relations'].keys():
                                        for relation in result['relations'][relation_types[t.reltype]]:
                                            t.text = f"{relation['lemma']}:{relation['uri']}={relation['morpho']}"
                                            yield t
                        else:
                            # query may be provided as lemma:uri=morpho
                            if all(re.match(r"(\w+)(?::([A-z0-9]+))?(?:=(.+))?", text).groups()):
                                t.text = text
                                yield t
                            else:
                                keys = ['lemma', 'uri', 'morpho']
                                kwargs = {
                                    k: v
                                    for k, v in zip(
                                        keys,
                                        re.search(r"(\w+)(?::([A-z0-9]+))?(?:=(.+))?", text).groups()
                                    )
                                }
                                if kwargs['uri'] is not None:
                                    results = LWN.lemmas_by_uri(kwargs['uri'])
                                else:
                                    kwargs.pop('uri')
                                    results = LWN.lemmas(**kwargs)

                                if results:
                                    for result in results:
                                        t.text = f"{result['lemma']}:{result['uri']}={result['morpho']}"
                                        yield t
                                else:
                                    yield t
