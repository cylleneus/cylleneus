# coding=utf-8

# Copyright 2007 Matt Chaput. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY MATT CHAPUT ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL MATT CHAPUT OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of Matt Chaput.

import copy
import re
from itertools import chain

from cylleneus.engine.analysis.acore import Composable
from cylleneus.lang import iso_639
from cylleneus.lang.morpho import leipzig2wn

from latinwordnet import LatinWordNet
from multiwordnet.wordnet import WordNet
from cylleneus.engine.compat import next
from whoosh.util.text import rcompile

LWN = LatinWordNet()

# Default list of stop words (words so common it's usually wasteful to index
# them). This list is used by the StopFilter class, which allows you to supply
# an optional list to override this one.

STOP_WORDS = frozenset(
    (
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "can",
        "for",
        "from",
        "have",
        "if",
        "in",
        "is",
        "it",
        "may",
        "not",
        "of",
        "on",
        "or",
        "tbd",
        "that",
        "the",
        "this",
        "to",
        "us",
        "we",
        "when",
        "will",
        "with",
        "yet",
        "you",
        "your",
    )
)


# Simple pattern for filtering URLs, may be useful

url_pattern = rcompile(
    """
(
    [A-Za-z+]+://          # URL protocol
    \\S+?                  # URL body
    (?=\\s|[.]\\s|$|[.]$)  # Stop at space/end, or a dot followed by space/end
) | (                      # or...
    \w+([:.]?\w+)*         # word characters, with opt. internal colons/dots
)
""",
    verbose=True,
)


# Filters


class Filter(Composable):
    """Base class for Filter objects. A Filter subclass must implement a
    filter() method that takes a single argument, which is an iterator of Token
    objects, and yield a series of Token objects in return.

    Filters that do morphological transformation of tokens (e.g. stemming)
    should set their ``is_morph`` attribute to True.
    """

    def __eq__(self, other):
        return (
            other
            and self.__class__ is other.__class__
            and self.__dict__ == other.__dict__
        )

    def __ne__(self, other):
        return not self == other

    def __call__(self, tokens):
        raise NotImplementedError


class PassFilter(Filter):
    """An identity filter: passes the tokens through untouched.
    """

    def __call__(self, tokens):
        return tokens


class LoggingFilter(Filter):
    """Prints the contents of every filter that passes through as a debug
    log entry.
    """

    def __init__(self, logger=None):
        """
        :param target: the logger to use. If omitted, the "
            logger is used.
        """

        if logger is None:
            import logging

            logger = logging.getLogger("")
        self.logger = logger

    def __call__(self, tokens):
        logger = self.logger
        for t in tokens:
            logger.debug(repr(t))
            yield t


class MultiFilter(Filter):
    """Chooses one of two or more sub-filters based on the 'mode' attribute
    of the token stream.
    """

    default_filter = PassFilter()

    def __init__(self, **kwargs):
        """Use keyword arguments to associate mode attribute values with
        instantiated filters.

        >>> iwf_for_index = IntraWordFilter(mergewords=True, mergenums=False)
        >>> iwf_for_query = IntraWordFilter(mergewords=False, mergenums=False)
        >>> mf = MultiFilter(index=iwf_for_index, query=iwf_for_query)

        This class expects that the value of the mode attribute is consistent
        among all tokens in a token stream.
        """
        self.filters = kwargs

    def __eq__(self, other):
        return (
            other
            and self.__class__ is other.__class__
            and self.filters == other.filters
        )

    def __call__(self, tokens):
        # Only selects on the first token
        t = next(tokens)
        filter = self.filters.get(t.mode, self.default_filter)
        return filter(chain([t], tokens))


class TeeFilter(Filter):
    """Interleaves the results of two or more filters (or filter chains).

    NOTE: because it needs to create copies of each token for each sub-filter,
    this filter is quite slow.

    >>> target = "ALFA BRAVO CHARLIE"
    >>> # In one branch, we'll lower-case the tokens
    >>> f1 = LowercaseFilter()
    >>> # In the other branch, we'll reverse the tokens
    >>> f2 = ReverseTextFilter()
    >>> ana = RegexTokenizer(r"\S+") | TeeFilter(f1, f2)
    >>> [token.text for token in ana(target)]
    ["alfa", "AFLA", "bravo", "OVARB", "charlie", "EILRAHC"]

    To combine the incoming token stream with the output of a filter chain, use
    ``TeeFilter`` and make one of the filters a :class:`PassFilter`.

    >>> f1 = PassFilter()
    >>> f2 = BiWordFilter()
    >>> ana = RegexTokenizer(r"\S+") | TeeFilter(f1, f2) | LowercaseFilter()
    >>> [token.text for token in ana(target)]
    ["alfa", "alfa-bravo", "bravo", "bravo-charlie", "charlie"]
    """

    def __init__(self, *filters):
        if len(filters) < 2:
            raise Exception("TeeFilter requires two or more filters")
        self.filters = filters

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__ and self.filters == other.fitlers
        )

    def __call__(self, tokens):
        from itertools import tee

        count = len(self.filters)
        # Tee the token iterator and wrap each teed iterator with the
        # corresponding filter
        gens = [
            filter(t.copy() for t in gen)
            for filter, gen in zip(self.filters, tee(tokens, count))
        ]
        # Keep a count of the number of running iterators
        running = count
        while running:
            for i, gen in enumerate(gens):
                if gen is not None:
                    try:
                        yield next(gen)
                    except StopIteration:
                        gens[i] = None
                        running -= 1


class ReverseTextFilter(Filter):
    """Reverses the text of each token.

    >>> ana = RegexTokenizer() | ReverseTextFilter()
    >>> [token.text for token in ana("hello there")]
    ["olleh", "ereht"]
    """

    def __call__(self, tokens):
        for t in tokens:
            t.text = t.text[::-1]
            yield t


class LowercaseFilter(Filter):
    """Uses unicode.lower() to lowercase token text.

    >>> rext = RegexTokenizer()
    >>> stream = rext("This is a TEST")
    >>> [token.text for token in LowercaseFilter(stream)]
    ["this", "is", "a", "test"]
    """

    def __call__(self, tokens):
        for t in tokens:
            t.text = t.text.lower()
            yield t


class StripFilter(Filter):
    """Calls unicode.strip() on the token text.
    """

    def __call__(self, tokens):
        for t in tokens:
            t.text = t.text.strip()
            yield t


class StopFilter(Filter):
    """Marks "stop" words (words too common to index) in the stream (and by
    default removes them).

    Make sure you precede this filter with a :class:`LowercaseFilter`.

    >>> stopper = RegexTokenizer() | StopFilter()
    >>> [token.text for token in stopper(u"this is a test")]
    ["test"]
    >>> es_stopper = RegexTokenizer() | StopFilter(lang="es")
    >>> [token.text for token in es_stopper(u"el lapiz es en la mesa")]
    ["lapiz", "mesa"]

    The list of available languages is in `whoosh.lang.languages`.
    You can use :func:`whoosh.lang.has_stopwords` to check if a given language
    has a stop word list available.
    """

    def __init__(
        self,
        stoplist=STOP_WORDS,
        minsize=2,
        maxsize=None,
        renumber=True,
        lang=None,
    ):
        """
        :param stoplist: A collection of words to remove from the stream.
            This is converted to a frozenset. The default is a list of
            common English stop words.
        :param minsize: The minimum length of token texts. Tokens with
            text smaller than this will be stopped. The default is 2.
        :param maxsize: The maximum length of token texts. Tokens with text
            larger than this will be stopped. Use None to allow any length.
        :param renumber: Change the 'pos' attribute of unstopped tokens
            to reflect their position with the stopped words removed.
        :param lang: Automatically get a list of stop words for the given
            language
        """

        stops = set()
        if stoplist:
            stops.update(stoplist)
        if lang:
            from whoosh.lang import stopwords_for_language

            stops.update(stopwords_for_language(lang))

        self.stops = frozenset(stops)
        self.min = minsize
        self.max = maxsize
        self.renumber = renumber

    def __eq__(self, other):
        return (
            other
            and self.__class__ is other.__class__
            and self.stops == other.stops
            and self.min == other.min
            and self.renumber == other.renumber
        )

    def __call__(self, tokens):
        stoplist = self.stops
        minsize = self.min
        maxsize = self.max
        renumber = self.renumber

        pos = None
        for t in tokens:
            text = t.text
            if (
                len(text) >= minsize
                and (maxsize is None or len(text) <= maxsize)
                and text not in stoplist
            ):
                # This is not a stop word
                if renumber and t.positions:
                    if pos is None:
                        pos = t.pos
                    else:
                        pos += 1
                        t.pos = pos
                t.stopped = False
                yield t
            else:
                # This is a stop word
                if not t.removestops:
                    # This IS a stop word, but we're not removing them
                    t.stopped = True
                    yield t


class CharsetFilter(Filter):
    """Translates the text of tokens by calling unicode.translate() using the
    supplied character mapping object. This is useful for case and accent
    folding.

    The ``whoosh.support.charset`` module has a useful map for accent folding.

    >>> from whoosh.support.charset import accent_map
    >>> retokenizer = RegexTokenizer()
    >>> chfilter = CharsetFilter(accent_map)
    >>> [t.text for t in chfilter(retokenizer(u'café'))]
    [u'cafe']

    Another way to get a character mapping object is to convert a Sphinx
    charset table file using
    :func:`whoosh.support.charset.charset_table_to_dict`.

    >>> from whoosh.support.charset import charset_table_to_dict
    >>> from whoosh.support.charset import default_charset
    >>> retokenizer = RegexTokenizer()
    >>> charmap = charset_table_to_dict(default_charset)
    >>> chfilter = CharsetFilter(charmap)
    >>> [t.text for t in chfilter(retokenizer(u'Stra\\xdfe'))]
    [u'strase']

    The Sphinx charset table format is described at
    http://www.sphinxsearch.com/docs/current.html#conf-charset-table.
    """

    __inittypes__ = dict(charmap=dict)

    def __init__(self, charmap):
        """
        :param charmap: a dictionary mapping from integer character numbers to
            unicode characters, as required by the unicode.translate() method.
        """

        self.charmap = charmap

    def __eq__(self, other):
        return (
            other
            and self.__class__ is other.__class__
            and self.charmap == other.charmap
        )

    def __call__(self, tokens):
        assert hasattr(tokens, "__iter__")
        charmap = self.charmap
        for t in tokens:
            t.text = t.text.translate(charmap)
            yield t


class DelimitedAttributeFilter(Filter):
    """Looks for delimiter characters in the text of each token and stores the
    data after the delimiter in a named attribute on the token.

    The defaults are set up to use the ``^`` character as a delimiter and store
    the value after the ``^`` as the boost for the token.

    >>> daf = DelimitedAttributeFilter(delimiter="^", attribute="boost")
    >>> ana = RegexTokenizer("\\\\S+") | DelimitedAttributeFilter()
    >>> for t in ana(u("image render^2 file^0.5"))
    ...    print("%r %f" % (t.text, t.boost))
    'image' 1.0
    'render' 2.0
    'file' 0.5

    Note that you need to make sure your tokenizer includes the delimiter and
    data as part of the token!
    """

    def __init__(
        self, delimiter="^", attribute="boost", default=1.0, type=float
    ):
        """
        :param delimiter: a string that, when present in a token's text,
            separates the actual text from the "data" payload.
        :param attribute: the name of the attribute in which to store the
            data on the token.
        :param default: the value to use for the attribute for tokens that
            don't have delimited data.
        :param type: the type of the data, for example ``str`` or ``float``.
            This is used to convert the string value of the data before
            storing it in the attribute.
        """

        self.delim = delimiter
        self.attr = attribute
        self.default = default
        self.type = type

    def __eq__(self, other):
        return (
            other
            and self.__class__ is other.__class__
            and self.delim == other.delim
            and self.attr == other.attr
            and self.default == other.default
        )

    def __call__(self, tokens):
        delim = self.delim
        attr = self.attr
        default = self.default
        type_ = self.type

        for t in tokens:
            text = t.text
            pos = text.find(delim)
            if pos > -1:
                setattr(t, attr, type_(text[pos + 1:]))
                if t.chars:
                    t.endchar -= len(t.text) - pos
                t.text = text[:pos]
            else:
                setattr(t, attr, default)

            yield t


class SubstitutionFilter(Filter):
    """Performs a regular expression substitution on the token text.

    This is especially useful for removing text from tokens, for example
    hyphens::

        ana = RegexTokenizer(r"\\S+") | SubstitutionFilter("-", "")

    Because it has the full power of the re.sub() method behind it, this filter
    can perform some fairly complex transformations. For example, to take
    tokens like ``'a=b', 'c=d', 'e=f'`` and change them to ``'b=a', 'd=c',
    'f=e'``::

        # Analyzer that swaps the text on either side of an equal sign
        rt = RegexTokenizer(r"\\S+")
        sf = SubstitutionFilter("([^/]*)/(./*)", r"\\2/\\1")
        ana = rt | sf
    """

    def __init__(self, pattern, replacement):
        """
        :param pattern: a pattern string or compiled regular expression object
            describing the text to replace.
        :param replacement: the substitution text.
        """

        self.pattern = rcompile(pattern)
        self.replacement = replacement

    def __eq__(self, other):
        return (
            other
            and self.__class__ is other.__class__
            and self.pattern == other.pattern
            and self.replacement == other.replacement
        )

    def __call__(self, tokens):
        pattern = self.pattern
        replacement = self.replacement

        for t in tokens:
            t.text = pattern.sub(replacement, t.text)
            yield t


class CachedLemmaFilter(Filter):
    is_morph = True

    def __init__(self, cached=True, **kwargs):
        super(CachedLemmaFilter, self).__init__()
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
                    if t.text:
                        text = t.text
                        results = LWN.lemmatize(text)
                        if results:
                            for i, lemma in enumerate(results):
                                t.morpho = (
                                    f"{lemma['lemma']['morpho']}::{lemma['lemma']['uri']}:{i}>"
                                    f"{' '.join(lemma['morpho'])}"
                                )
                                t.text = f"{lemma['lemma']['lemma']}:{lemma['lemma']['uri']}={lemma['lemma']['morpho']}"
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
                                    results = LWN.lemmas_by_uri(
                                        kwargs["uri"]
                                    ).relations
                                else:
                                    kwargs.pop("uri")
                                    results = LWN.lemmas(**kwargs).relations
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
                                    if t.reltype in result["relations"].keys():
                                        for relation in result["relations"][
                                            t.reltype
                                        ]:
                                            t.text = f"{relation['lemma']}:{relation['uri']}={relation['morpho']}"
                                            yield t
                        else:
                            # query may be provided as lemma:uri=morpho
                            if all(
                                re.match(
                                    r"([\w\-]+)(?::([A-z0-9]+))?(?:=(.+))?",
                                    text,
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
                                            r"([\w\-]+)(?::([A-z0-9]+))?(?:=(.+))?",
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


class AnnotationFilter(Filter):
    is_morph = True

    def __init__(self, **kwargs):
        super(AnnotationFilter, self).__init__()
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
                text = t.morpho
                if text:
                    morpho, annotations = text.split(">")
                    r = morpho.split("::")[1]
                    uri, n = r.split(":")
                    for i, annotation in enumerate(annotations.split()):
                        t.text = f"{annotation}::{uri}:{n}:{i}"
                        yield t

                        for j, v in enumerate(annotation):
                            if v != "-":
                                text = f"{'-' * j}{v}{'-' * (9 - j)}::{uri}:{n}:{i}"
                                t.text = text
                                yield t
            elif t.mode == "query":
                annotation = leipzig2wn(t.original)
                if annotation == "----------":
                    continue
                else:
                    for i, v in enumerate(annotation):
                        if v != "-":
                            text = f"{'-' * i}{v}{'-' * (9 - i)}"
                            t.text = f"{text}::([\w\d$]+):(\d+):(\d+)$"
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
                if hasattr(t, "code"):
                    codes = t.code.split(" ")
                    if codes:
                        for code in codes:
                            if code:
                                t.text = code
                                yield t
            elif t.mode == "query":
                text = t.original

                if text:
                    if text.isnumeric():
                        results = LWN.semfields(code=text)
                    else:
                        q = text[1:]
                        results = LWN.semfields(english=q).search()
                    if results:
                        for result in results:
                            t.text = result["code"]
                            yield t


class CachedSynsetFilter(Filter):
    is_morph = True

    def __init__(self, **kwargs):
        super(CachedSynsetFilter, self).__init__()
        self._cache = None
        self._docix = None
        self.cached = True
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
                    text = t.text
                    if text:
                        keys = ["lemma", "uri", "morpho"]
                        kwargs = {
                            k: v
                            for k, v in zip(
                                keys,
                                re.search(
                                    r"(\w+)(?::([A-z0-9]+))?(?:=(.+))?", text
                                ).groups(),
                            )
                        }
                        if kwargs["uri"] is not None:
                            results = LWN.lemmas_by_uri(kwargs["uri"]).synsets
                        else:
                            kwargs.pop("uri")
                            results = LWN.lemmas(**kwargs).synsets
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
                                lexical = True if t.reltype in ["\\", "/", "+c", "-c"] else False
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
                            result = LWN.synsets(pos, offset).relations
                            if t.reltype in result.keys():
                                for relation in result[t.reltype]:
                                    t.text = f"{relation['pos']}#{relation['offset']}"
                                    yield t
                        else:
                            yield t
                    elif t.text.startswith("="):
                        if t.fieldname == "semfield":
                            yield t
                        elif t.fieldname == "synset":
                            q = t.text[1:]
                            synsets = LWN.synsets(gloss=q).search()
                            for synset in synsets:
                                t.text = f"{synset['pos']}#{synset['offset']}"
                                yield t
                    else:
                        yield t


class CaseFilter(Filter):
    def __call__(self, tokens, **kwargs):
        for t in tokens:
            yield t

            if t.text.istitle():
                lower = t.text.lower()
                t.text = lower
            else:
                upper = t.text.title()
                t.text = upper
            yield t


class MappingFilter(Filter):
    is_morph = True

    def __init__(self, **kwargs):
        super(MappingFilter, self).__init__()
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
                source = t.source
                target = t.target
                figure = t.figure
                if figure and source and target:
                    if figure == "#":
                        text = f"{target.upper()} IS {source.upper()}"
                    elif figure == "~":
                        text = f"{source.upper()} FOR {target.upper()}"
                    else:
                        text = None
                    if (
                        text
                        and re.match(r"([\w\s]+) (IS|FOR) ([\w\s]+)", text)
                        and all(
                        re.match(
                            r"([\w\s]+) (IS|FOR) ([\w\s]+)", text
                        ).groups()
                    )
                    ):
                        t.text = text
                        yield t
            elif t.mode == "query":
                text = t.text
                if text and all(
                    re.match(
                        r"([\w\s]+|\*) (IS|(?:STANDS )?FOR) ([\w\s]+|\*)",
                        text,
                    ).groups()
                ):
                    yield t
