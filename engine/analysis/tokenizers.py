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
import string
from collections import abc, deque

import engine.analysis
from cltk.tokenize.latin_exceptions import latin_exceptions
from corpus.lasla import parse_bpn
from engine.analysis.acore import Composable, CylleneusToken
from lang.latin import compound, proper_names
from nltk.tokenize.punkt import PunktLanguageVars, PunktParameters, PunktSentenceTokenizer
from utils import flatten, roman_to_arabic
from whoosh.compat import text_type, u
from whoosh.util.text import rcompile

jvmap = str.maketrans('jv', 'iu', '')
punctuation = str.maketrans("", "", string.punctuation)

default_pattern = rcompile(r"\w+(\.?\w+)*")


# Tokenizers
class Tokenizer(Composable):
    """Base class for Tokenizers.
    """

    def __eq__(self, other):
        return other and self.__class__ is other.__class__


class IDTokenizer(Tokenizer):
    """Yields the entire input string as a single token. For use in indexed but
    untokenized fields, such as a document's path.

    >>> idt = IDTokenizer()
    >>> [token.text for token in idt("/a/b 123 alpha")]
    ["/a/b 123 alpha"]
    """

    def __call__(self, value, positions=False, chars=False,
                 keeporiginal=False, removestops=True,
                 start_pos=0, start_char=0, mode='', **kwargs):
        assert isinstance(value, text_type), "%r is not unicode" % value
        t = CylleneusToken(positions, chars, removestops=removestops, mode=mode,
                  **kwargs)
        t.text = value
        t.boost = 1.0

        if keeporiginal:
            t.original = value
        if positions:
            t.pos = start_pos + 1
        if chars:
            t.startchar = start_char
            t.endchar = start_char + len(value)
        yield t


class RegexTokenizer(Tokenizer):
    """
    Uses a regular expression to extract tokens from text.

    >>> rex = RegexTokenizer()
    >>> [token.text for token in rex(u("hi there 3.141 big-time under_score"))]
    ["hi", "there", "3.141", "big", "time", "under_score"]
    """

    def __init__(self, expression=default_pattern, gaps=False):
        """
        :param expression: A regular expression object or string. Each match
            of the expression equals a token. Group 0 (the entire matched text)
            is used as the text of the token. If you require more complicated
            handling of the expression match, simply write your own tokenizer.
        :param gaps: If True, the tokenizer *splits* on the expression, rather
            than matching on the expression.
        """

        self.expression = rcompile(expression)
        self.gaps = gaps

    def __eq__(self, other):
        if self.__class__ is other.__class__:
            if self.expression.pattern == other.expression.pattern:
                return True
        return False

    def __call__(self, value, positions=False, chars=False, keeporiginal=False,
                 removestops=True, start_pos=0, start_char=0, tokenize=True,
                 mode='', **kwargs):
        """
        :param value: The unicode string to tokenize.
        :param positions: Whether to record token positions in the token.
        :param chars: Whether to record character offsets in the token.
        :param start_pos: The position number of the first token. For example,
            if you set start_pos=2, the tokens will be numbered 2,3,4,...
            instead of 0,1,2,...
        :param start_char: The offset of the first character of the first
            token. For example, if you set start_char=2, the text "aaa bbb"
            will have chars (2,5),(6,9) instead (0,3),(4,7).
        :param tokenize: if True, the text should be tokenized.
        """

        assert isinstance(value, text_type), "%s is not unicode" % repr(value)

        t = CylleneusToken(positions, chars, removestops=removestops, mode=mode,
                  **kwargs)
        if not tokenize:
            t.original = t.text = value
            t.boost = 1.0
            if positions:
                t.pos = start_pos
            if chars:
                t.startchar = start_char
                t.endchar = start_char + len(value)
            yield t
        elif not self.gaps:
            # The default: expression matches are used as tokens
            for pos, match in enumerate(self.expression.finditer(value)):
                t.text = match.group(0)
                t.boost = 1.0
                if keeporiginal:
                    t.original = t.text
                t.stopped = False
                if positions:
                    t.pos = start_pos + pos
                if chars:
                    t.startchar = start_char + match.start()
                    t.endchar = start_char + match.end()
                yield t
        else:
            # When gaps=True, iterate through the matches and
            # yield the text between them.
            prevend = 0
            pos = start_pos
            for match in self.expression.finditer(value):
                start = prevend
                end = match.start()
                text = value[start:end]
                if text:
                    t.text = text
                    t.boost = 1.0
                    if keeporiginal:
                        t.original = t.text
                    t.stopped = False
                    if positions:
                        t.pos = pos
                        pos += 1
                    if chars:
                        t.startchar = start_char + start
                        t.endchar = start_char + end

                    yield t

                prevend = match.end()

            # If the last "gap" was before the end of the text,
            # yield the last bit of text as a final token.
            if prevend < len(value):
                t.text = value[prevend:]
                t.boost = 1.0
                if keeporiginal:
                    t.original = t.text
                t.stopped = False
                if positions:
                    t.pos = pos
                if chars:
                    t.startchar = prevend
                    t.endchar = len(value)
                yield t


class CharsetTokenizer(Tokenizer):
    """Tokenizes and translates text according to a character mapping object.
    Characters that map to None are considered token break characters. For all
    other characters the map is used to translate the character. This is useful
    for case and accent folding.

    This tokenizer loops character-by-character and so will likely be much
    slower than :class:`RegexTokenizer`.

    One way to get a character mapping object is to convert a Sphinx charset
    table file using :func:`whoosh.support.charset.charset_table_to_dict`.

    >>> from whoosh.support.charset import charset_table_to_dict
    >>> from whoosh.support.charset import default_charset
    >>> charmap = charset_table_to_dict(default_charset)
    >>> chtokenizer = CharsetTokenizer(charmap)
    >>> [t.text for t in chtokenizer(u'Stra\\xdfe ABC')]
    [u'strase', u'abc']

    The Sphinx charset table format is described at
    http://www.sphinxsearch.com/docs/current.html#conf-charset-table.
    """

    __inittype__ = dict(charmap=str)

    def __init__(self, charmap):
        """
        :param charmap: a mapping from integer character numbers to unicode
            characters, as used by the unicode.translate() method.
        """
        self.charmap = charmap

    def __eq__(self, other):
        return (other
                and self.__class__ is other.__class__
                and self.charmap == other.charmap)

    def __call__(self, value, positions=False, chars=False, keeporiginal=False,
                 removestops=True, start_pos=0, start_char=0, tokenize=True,
                  mode='', **kwargs):
        """
        :param value: The unicode string to tokenize.
        :param positions: Whether to record token positions in the token.
        :param chars: Whether to record character offsets in the token.
        :param start_pos: The position number of the first token. For example,
            if you set start_pos=2, the tokens will be numbered 2,3,4,...
            instead of 0,1,2,...
        :param start_char: The offset of the first character of the first
            token. For example, if you set start_char=2, the text "aaa bbb"
            will have chars (2,5),(6,9) instead (0,3),(4,7).
        :param tokenize: if True, the text should be tokenized.
        """

        assert isinstance(value, text_type), "%r is not unicode" % value

        t = CylleneusToken(positions, chars, removestops=removestops, mode=mode,
                  **kwargs)
        if not tokenize:
            t.original = t.text = value
            t.boost = 1.0
            if positions:
                t.pos = start_pos
            if chars:
                t.startchar = start_char
                t.endchar = start_char + len(value)
            yield t
        else:
            text = u("")
            charmap = self.charmap
            pos = start_pos
            startchar = currentchar = start_char
            for char in value:
                tchar = charmap[ord(char)]
                if tchar:
                    text += tchar
                else:
                    if currentchar > startchar:
                        t.text = text
                        t.boost = 1.0
                        if keeporiginal:
                            t.original = t.text
                        if positions:
                            t.pos = pos
                            pos += 1
                        if chars:
                            t.startchar = startchar
                            t.endchar = currentchar
                        yield t
                    startchar = currentchar + 1
                    text = u("")

                currentchar += 1

            if currentchar > startchar:
                t.text = value[startchar:currentchar]
                t.boost = 1.0
                if keeporiginal:
                    t.original = t.text
                if positions:
                    t.pos = pos
                if chars:
                    t.startchar = startchar
                    t.endchar = currentchar
                yield t


def SpaceSeparatedTokenizer():
    """Returns a RegexTokenizer that splits tokens by whitespace.

    >>> sst = SpaceSeparatedTokenizer()
    >>> [token.text for token in sst("hi there big-time, what's up")]
    ["hi", "there", "big-time,", "what's", "up"]
    """

    return RegexTokenizer(r"[^ \t\r\n]+")


def CommaSeparatedTokenizer():
    """Splits tokens by commas.

    Note that the tokenizer calls unicode.strip() on each match of the regular
    expression.

    >>> cst = CommaSeparatedTokenizer()
    >>> [token.text for token in cst("hi there, what's , up")]
    ["hi there", "what's", "up"]
    """

    from whoosh.analysis.filters import StripFilter

    return RegexTokenizer(r"[^,]+") | StripFilter()


class PathTokenizer(Tokenizer):
    """A simple tokenizer that given a string ``"/a/b/c"`` yields tokens
    ``["/a", "/a/b", "/a/b/c"]``.
    """

    def __init__(self, expression="[^/]+"):
        self.expr = rcompile(expression)

    def __call__(self, value, positions=False, start_pos=0, **kwargs):
         assert isinstance(value, text_type), "%r is not unicode" % value
         token = CylleneusToken(positions, **kwargs)
         pos = start_pos
         for match in self.expr.finditer(value):
             token.text = value[:match.end()]
             if positions:
                 token.pos = pos
                 pos += 1
             yield token


def nested_dict_iter(nested, path=None):
    if not path:
        path = []
    for i in nested.keys():
        local_path = path[:]
        local_path.append(i)
        if isinstance(nested[i], abc.Mapping):
            yield from nested_dict_iter(nested[i], local_path)
        else:
            yield local_path, nested[i]

def matchcase(word):
    def replace(m):
        text = m.group()
        if text.isupper():
            return word.upper()
        elif text.islower():
            return word.lower()
        elif text[0].isupper():
            return word.capitalize()
        else:
            return word
    return replace

replacements = {
    'mecum': ['cum', 'me'],
    'tecum': ['cum', 'te'],
    'secum': ['cum', 'se'],
    'nobiscum': ['cum', 'nobis'],
    'vobiscum': ['cum', 'vobis'],
    'quocum': ['cum', 'quo'],
    'quacum': ['cum', 'qua'],
    'quicum': ['cum', 'qui'],
    'quibuscum': ['cum', 'quibus'],
    'sodes': ['si', 'audes'],
    'satin': ['satis', '-ne'],
    'scin': ['scis', '-ne'],
    'sultis': ['si', 'vultis'],
    'similist': ['similis', 'est'],
    'qualist': ['qualis', 'est'],
    'C.': ['Gaius'],
    'L.': ['Lucius'],
    'M.': ['Marcus'],
    'A.': ['Aulus'],
    'Cn.': ['Gnaeus'],
    'Sp.': ['Spurius'],
    "M'.": ['Manius'],
    'Ap.': ['Appius'],
    'Agr.': ['Agrippa'],
    'K.': ['Caeso'],
    'D.': ['Decimus'],
    'F.': ['Faustus'],
    'Mam.': ['Mamercus'],
    'N.': ['Numerius'],
    'Oct.': ['Octavius'],
    'Opet.': ['Opiter'],
    'Paul.': ['Paullus'],
    'Post.': ['Postumus'],
    'Pro.': ['Proculus'],
    'P.': ['Publius'],
    'Q.': ['Quintus'],
    'Sert.': ['Sertor'],
    'Ser.': ['Servius'],
    'Sex.': ['Sextus'],
    'S.': ['Spurius'],
    'St.': ['Statius'],
    'Ti.': ['Tiberius'],
    'T.': ['Titus'],
    'V.': ['Vibius'],
    'Vol.': ['Volesus'],
    'Vop.': ['Vopiscus'],
    'a.d.': ['ante', 'diem'],
    'a.': ['ante'],
    'd.': ['diem'],
    'Kal.': ['Kalendas'],
    'Id.': ['Idus'],
    'Non.': ['Nonas'],
    'Kal': ['Kalendas'],
    'Kalend': ['Kalendas'],
    'Id': ['Idus'],
    'Non': ['Nonas'],
    'Ianuar': ['Ianuarias'],
    'Febr': ['Februarias'],
    'Septembr': ['Septembris'],
    'Octobr': ['Octobris'],
    'Novembr': ['Novembris'],
    'Decembr': ['Decembris'],
    'Quint.': ['Quintilis'],
    'Sextil.': ['Sextilis'],
    'pr': ['pridie'],
    'Pr.': ['pridie'],
    'HS': ['sestertios'],
}

editorial = {
    'ante quam': 'antequam',
    'post quam': 'postquam',
    'me hercule': 'mehercule',
    'quam ob rem': 'quamobrem',
    'nihilo setius': 'nihilosetius',
    'nihilo secius': 'nihilosecius',
}

punkt_param = PunktParameters()
abbreviations = ['c', 'l', 'm', 'p', 'q', 't', 'ti', 'sex', 'a', 'd', 'cn', 'sp', "m'", 'ser', 'ap', 'n',
                 'v', 'k', 'mam', 'post', 'f', 'oct', 'opet', 'paul', 'pro', 'sert', 'st', 'sta', 'v', 'vol', 'vop']
punkt_param.abbrev_types = set(abbreviations)
sent_tokenizer = PunktSentenceTokenizer(punkt_param)

# [] and <> can appear within words as editorial conventions
class PunktLatinVars(PunktLanguageVars):
    _re_non_word_chars = r"(?:[?!)\";}\*:@\'\({])"
    """Characters that cannot appear within words"""

    _word_tokenize_fmt = r'''(
        %(MultiChar)s
        |
        (?=%(WordStart)s)\S+?                   # Accept word characters until end is found
        (?=                                     # Sequences marking a word's end
            \s|                                 # White-space
            $|                                  # End-of-string
            %(NonWord)s|%(MultiChar)s|          # Punctuation
            ,(?=$|\s|%(NonWord)s|%(MultiChar)s) # Comma if at end of word
        )
        |
        \S                                      
    )'''
word_tokenizer = PunktLatinVars()

class PunktLatinCharsVars(PunktLanguageVars):
    _re_non_word_chars = r"(?:[\[\]<>?!)\";}\*:@\({])" # remove []<>? ' can appear in, e.g., adgressu's
    """Characters that cannot appear within words"""

    _word_tokenize_fmt = r'''(
        %(MultiChar)s
        |
        (?=%(WordStart)s)\S+?                   # Accept word characters until end is found
        (?=                                     # Sequences marking a word's end
            \s|                                 # White-space
            $|                                  # End-of-string
            %(NonWord)s|%(MultiChar)s|          # Punctuation
            ,(?=$|\s|%(NonWord)s|%(MultiChar)s) # Comma if at end of word
        )
        |
        \s                                      # normally \S!
        |%(NonWord)s|%(MultiChar)s|,            # tokenize punctuation
    )'''

enclitics = ['que', 'ne', 'n', 'ue', 've', 'st', "'s"]
exceptions = list(set(enclitics + latin_exceptions + ['duplione', 'declinatione', 'altitudine', 'contentione', 'Ion']))


class CachedPlainTextTokenizer(Tokenizer):
    def __init__(self, **kwargs):
        super(CachedPlainTextTokenizer, self).__init__()
        self.__dict__.update(**kwargs)
        self._cache = None
        self._docix = 0

    @property
    def cache(self):
        return copy.deepcopy(self._cache)

    def __call__(self, value: str, positions=True, chars=True,
                 keeporiginal=True, removestops=True, tokenize=True,
                 start_pos=0, start_char=0, mode='', **kwargs):
        if self._cache and kwargs.get('docix', None) == self._docix:
            yield from self.cache
        else:
            t = CylleneusToken(positions, chars, removestops=removestops, mode=mode, **kwargs)

            if t.mode == 'query':
                t.original = t.text = value
                yield t
                t.text = value.translate(jvmap)
                yield t
            else:
                if not tokenize:
                    t.original = t.text = value
                    t.boost = 1.0
                    if positions:
                        t.pos = start_pos
                    if chars:
                        t.startchar = start_char
                        t.endchar = start_char + len(value)
                    yield t
                else:
                    self._cache = []
                    self._docix = kwargs.get('docix', 0)

                    sents = sent_tokenizer.tokenize(value)
                    stopchars = str.maketrans('', '', string.punctuation.replace('-', ''))

                    tokens = []
                    for sent in sents:
                        temp_tokens = word_tokenizer.word_tokenize(sent)

                        if temp_tokens:
                            if temp_tokens[0].replace('j', 'i').replace('v', 'u') not in proper_names.proper_names:
                                temp_tokens[0] = temp_tokens[0]

                            if temp_tokens[-1].endswith('.'):
                                final_word = temp_tokens[-1][:-1]
                                del temp_tokens[-1]
                                temp_tokens += [final_word, '.']

                            skipflag = False
                            for ix, token in enumerate(temp_tokens):
                                if not skipflag:
                                    ppp = compound.is_ppp(token)
                                    if ppp:
                                        copula = compound.is_copula(temp_tokens[ix+1])
                                        if copula and ppp[1] == copula[2]:
                                            tense, mood, number, i = copula
                                            token = f"{token} {compound.copula[tense][mood][number][i]}"
                                            tokens.append(token)
                                            skipflag = True
                                        else:
                                            tokens.append(token)
                                    else:
                                        tokens.append(token)
                                else:
                                    skipflag = False
                    for pos, token in enumerate(tokens):
                        t.boost = 1.0
                        if keeporiginal:
                            t.original = token
                        t.stopped = False
                        if positions:
                            t.pos = start_pos + pos
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
                        if not token:
                            start_char += 1
                            continue

                        is_enclitic = False
                        if token not in exceptions:
                            if t.original in replacements:
                                for subtoken in replacements[t.original]:
                                    t.text = subtoken
                                    t.startchar = start_char
                                    t.endchar = start_char + original_length
                                    if mode == 'index': self._cache.append(copy.copy(t))
                                    yield t
                                start_char += original_length + 1
                                continue

                            if re.match(r"(?:\w+) (?:\w+)", token):
                                ppp, copula = token.split(' ')
                                t.text = ppp.lower()
                                t.startchar = start_char
                                t.endchar = start_char + len(ppp)
                                if mode == 'index': self._cache.append(copy.copy(t))
                                yield t
                                t.text = copula.lower()
                                t.startchar = start_char + len(ppp) + 1
                                t.endchar = start_char + len(ppp) + 1 + len(copula)
                                if mode == 'index': self._cache.append(copy.copy(t))
                                yield t
                                start_char += original_length + 1
                                continue

                            for enclitic in enclitics:
                                if token.lower().endswith(enclitic):
                                    if enclitic == 'ne':
                                        t.text = (token[:-len(enclitic)]).lower()
                                        t.startchar = start_char
                                        t.endchar = start_char + (len(token) - len(enclitic))
                                        if mode == 'index': self._cache.append(copy.copy(t))
                                        yield t
                                        t.text = 'ne'
                                        t.startchar = start_char + len(token[:-len(enclitic)])
                                        t.endchar = start_char + len(token[:-len(enclitic)]) + len(enclitic)
                                        if mode == 'index': self._cache.append(copy.copy(t))
                                        yield t
                                    elif enclitic == 'n':
                                        t.text = (token[:-len(enclitic)] + 's').lower()
                                        t.startchar = start_char
                                        t.endchar = start_char + (len(token) + 1) - len(enclitic)
                                        if mode == 'index': self._cache.append(copy.copy(t))
                                        yield t
                                        t.text = 'ne'
                                        t.startchar = start_char + len(token[:-len(enclitic)])
                                        t.endchar = start_char + len(token[:-len(enclitic)]) + len(enclitic)
                                        if mode == 'index': self._cache.append(copy.copy(t))
                                        yield t
                                    elif enclitic == 'st':
                                        if token.endswith('ust'):
                                            t.text = (token[:-len(enclitic) + 1]).lower()
                                            t.startchar = start_char
                                            t.endchar = start_char + len(token[:-len(enclitic) + 1]) - len(enclitic)
                                            if mode == 'index': self._cache.append(copy.copy(t))
                                            yield t
                                            t.text = 'est'
                                            t.startchar = start_char + len(token[:-len(enclitic) + 1])
                                            t.endchar = start_char + len(token[:-len(enclitic) + 1]) + len(enclitic)
                                            if mode == 'index': self._cache.append(copy.copy(t))
                                            yield t
                                        else:
                                            t.text = (token[:-len(enclitic)]).lower()
                                            t.startchar = start_char
                                            t.endchar = start_char + len(token[:-len(enclitic)]) - len(enclitic)
                                            if mode == 'index': self._cache.append(copy.copy(t))
                                            yield t
                                            t.text = 'est'
                                            t.startchar = start_char + len(token[:-len(enclitic) + 1])
                                            t.endchar = start_char + len(token[:-len(enclitic) + 1]) + len(enclitic)
                                            if mode == 'index': self._cache.append(copy.copy(t))
                                            yield t
                                    elif enclitic == "'s":
                                        t.text = token + 's'
                                        t.startchar = start_char
                                        t.endchar = start_char + len(token)
                                        if mode == 'index': self._cache.append(copy.copy(t))
                                        yield t
                                        t.text = 'es'
                                        t.startchar = start_char + len(token) + 1
                                        t.endchar = start_char + len(token) + len(enclitic)
                                        if mode == 'index': self._cache.append(copy.copy(t))
                                        yield t
                                    else:
                                        t.text = (token[:-len(enclitic)])
                                        t.startchar = start_char
                                        t.endchar = start_char + len(token[:-len(enclitic)])
                                        if mode == 'index': self._cache.append(copy.copy(t))
                                        yield t
                                        t.text = enclitic
                                        t.startchar = start_char + len(token[:-len(enclitic)])
                                        t.endchar = start_char + len(token[:-len(enclitic)]) + len(enclitic)
                                        if mode == 'index': self._cache.append(copy.copy(t))
                                        yield t
                                    is_enclitic = True
                                    break
                        if not is_enclitic:
                            t.text = token
                            if chars:
                                t.startchar = start_char + ldiff
                                t.endchar = start_char + original_length - rdiff  # - ndiff - rdiff
                            if mode == 'index': self._cache.append(copy.copy(t))
                            yield t
                        start_char += original_length + 1


class CachedPHI5Tokenizer(Tokenizer):
    def __init__(self, **kwargs):
        super(CachedPHI5Tokenizer, self).__init__()
        self.__dict__.update(**kwargs)
        self._cache = None
        self._docix = 0

    @property
    def cache(self):
        return copy.deepcopy(self._cache)

    def __call__(self, data, positions=True, chars=True,
                 keeporiginal=True, removestops=True, tokenize=True,
                 start_pos=0, start_char=0, mode='', **kwargs):
        if self._cache and kwargs.get('docix', None) == self._docix:
            yield from self.cache
        else:
            t = CylleneusToken(positions, chars, removestops=removestops, mode=mode, **kwargs)

            if t.mode == 'query':
                t.original = t.text = data.translate(jvmap)
                yield t
            else:
                if not tokenize:
                    t.original = t.text = data['text']
                    t.boost = 1.0
                    if positions:
                        t.pos = start_pos
                    if chars:
                        t.startchar = start_char
                        t.endchar = start_char + len(data['text'])
                    yield t
                else:
                    self._cache = []
                    self._docix = kwargs.get('docix', 0)

                    word_tokenizer = PunktLatinCharsVars()
                    stopchars = str.maketrans('', '',
                                              string.punctuation.replace('&', '').replace('^', '') + "†“”—\n\ŕ")

                    divs = { i: div.lower() for i, div in enumerate(data['meta'].split('-')) }

                    lines = iter(data['text'].split('\n'))
                    tpos = start_pos
                    xtitle = ytitle = ztitle = speaker = ''
                    buffer = deque()
                    for line in lines:
                        def parse_phi_line(_line):
                            result = []
                            nonlocal xtitle, ytitle, ztitle, speaker, buffer
                            try:
                                ref, text = _line.split('\t')
                            except ValueError:
                                result.append((None, None))
                            else:
                                v, w, x, y, z = ref.rstrip('.').split('.')
                                offset = 0
                                # d is a number, followed by -, t, a then possibly another number or . for a title
                                # d can be 'opinc' 'sedinc' 'dub', 'inc',
                                # c can be 'Summ'
                                if x == 't':
                                    xtitle = text.translate(stopchars).strip()
                                if y == 't':
                                    if z:
                                        ytitle = text.translate(stopchars).strip()
                                    else:
                                        speaker = text.translate(stopchars).strip()
                                    result.append((None, [text]))
                                elif z == 't':
                                    ztitle = text.translate(stopchars).strip()
                                    result.append((None, [text]))
                                elif '        {' in text:
                                    result.append((None, [text]))
                                else:
                                    temp_tokens = word_tokenizer.word_tokenize(text)
                                    if temp_tokens:
                                        if temp_tokens[0].replace('j', 'i').replace('v', 'u') not in proper_names.proper_names:
                                            temp_tokens[0] = temp_tokens[0].lower()

                                        if temp_tokens[-1].endswith('.') and temp_tokens[-1] != '. . .':
                                            final_word = temp_tokens[-1][:-1]
                                            del temp_tokens[-1]
                                            temp_tokens += [final_word, '.']

                                        if temp_tokens[-1].endswith('-'):
                                            buffer += list(parse_phi_line(next(lines)))
                                            new_ref, new_tokens = buffer.pop()
                                            merged_word = '2&' + temp_tokens[-1][:-1] + new_tokens[0]
                                            del temp_tokens[-1]
                                            temp_tokens += [merged_word]
                                            del new_tokens[0]
                                            if new_tokens:
                                                if new_tokens[0] in string.punctuation:
                                                    new_token = f"^1{new_tokens[0]}"
                                                    del new_tokens[0]
                                                    new_tokens.insert(0, new_token)
                                                buffer.appendleft((new_ref, new_tokens))

                                        for ix, token in enumerate(temp_tokens):
                                            if temp_tokens[ix] == '. . .':
                                                temp_tokens.insert(ix + 1, '&1')
                                            if '&' in token:
                                                ppp = compound.is_ppp(re.sub(r"[&\d]", '', token))
                                            else:
                                                ppp = compound.is_ppp(token)
                                            if ppp:
                                                if ix == len(temp_tokens) - 1:
                                                    if not buffer:
                                                        try:
                                                            buffer += list(parse_phi_line(next(lines)))
                                                        except StopIteration:
                                                            continue
                                                    if '&' in buffer[0][1][0]:
                                                        copula = compound.is_copula(buffer[0][1][0][2:])
                                                    else:
                                                        copula = compound.is_copula(buffer[0][1][0])
                                                else:
                                                    copula = compound.is_copula(temp_tokens[ix+1])


                                                if copula and ppp[1] == copula[2]:
                                                    tense, mood, number, i = copula
                                                    if buffer:
                                                        token = f"{token} &2{compound.copula[tense][mood][number][i]}"
                                                    else:
                                                        token = f"{token} {compound.copula[tense][mood][number][i]}"
                                                    del temp_tokens[ix]
                                                    if buffer:
                                                        del buffer[0][1][0]
                                                    else:
                                                        del temp_tokens[ix]
                                                    temp_tokens.insert(ix, token)
                                                    if ix != len(temp_tokens) - 1:
                                                        if temp_tokens[ix+1] in string.punctuation:
                                                            new_token = f"^1{temp_tokens[ix+1]} "
                                                            del temp_tokens[ix+1]
                                                            temp_tokens.insert(ix+1, new_token)
                                    if buffer:
                                        for i in range(len(buffer)):
                                            result.append(buffer.pop())
                                    result.append(((v, w, x, y, z), temp_tokens))
                            yield from result

                        result = list(parse_phi_line(line))
                        act = scene = None
                        for ref, tokens in reversed(result):
                            enjambed = False
                            if not ref and not tokens:
                                start_char += len(line) + 1
                                continue
                            elif not ref:
                                text = tokens[0].strip().strip('{}')
                                if re.match(r'[IVXLDMivxldm]+\.[IVXLDMivxldm]+', text):
                                    act, scene = text.split('.')
                                    act = str(roman_to_arabic(act))
                                    scene = str(roman_to_arabic(scene))
                                start_char += len(line.split('\t')[1]) + 1
                                continue
                            notoken = 0

                            skip = False
                            for line_pos, token in enumerate(tokens):
                                if token == '{' or token == '}':
                                    skip = not skip
                                    start_char += len(token)
                                    continue
                                if skip:
                                    speaker = token.replace('v', 'u')
                                    start_char += len(token)
                                    continue

                                offset = 0
                                line_pos -= notoken

                                meta = {}
                                #extra['meta'] = data['meta'].lower()
                                #setattr(t, 'meta', data['meta'].lower())
                                for i in range(len(divs)):
                                    meta[divs[len(divs) - (i + 1)]] = ref[-(5 - (5 - (i + 1)))].strip('t')
                                    #setattr(t, divs[len(divs) - (i + 1)], ref[-(5 - (5 - (i + 1)))].strip('t'))
                                    if xtitle:
                                        if len(divs) >= 3:
                                            meta[f"{divs[len(divs)-3]}_title"] = xtitle
                                            # setattr(t, f"{divs[len(divs)-3]}_title", xtitle)
                                    if ytitle:
                                        if len(divs) >= 2:
                                            meta[f"{divs[len(divs)-2]}_title"] = ytitle
                                            # setattr(t, f"{divs[len(divs)-2]}_title", ytitle)
                                    if ztitle:
                                        if len(divs) >= 1:
                                            meta[f"{divs[len(divs)-1]}_title"] = ztitle
                                            #setattr(t, f"{divs[len(divs)-1]}_title", ztitle)
                                if act:
                                    meta['act'] = act
                                if scene:
                                    meta['scene'] = scene
                                # if speaker:
                                #     t.speaker = speaker
                                t.boost = 1.0

                                pre = re.search(r"^\^(\d+?)", token)
                                if pre:
                                    start_char -= int(pre.group(1))
                                    token = re.sub(r"^\^\d+?", '', token)
                                pre = re.search(r"^&(\d+?)", token)
                                if pre:
                                    start_char += int(pre.group(1))
                                    token = re.sub(r"^&\d+?", '', token)
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
                                if not re.match(r"(?:[\d]&)?[\w]+\s(?:&[\d])?[\w]+", token):
                                    token = token.replace(' ', '')
                                if not token:
                                    start_char += original_length
                                    notoken += 1
                                    continue
                                else:
                                    if positions:
                                        meta['line_pos'] = line_pos
                                        t.pos = tpos
                                    t.meta = meta

                                    if token not in exceptions and token.lower() not in exceptions and re.sub(r"\d&|&\d", '', token) not in exceptions:
                                        if token in replacements: # t.original
                                            for subtoken in replacements[token]:
                                                t.text = subtoken.lower()
                                                t.startchar = start_char
                                                t.endchar = start_char + original_length
                                                if mode == 'index': self._cache.append(copy.copy(t))
                                                yield t
                                            start_char += original_length
                                            tpos += 1
                                            continue

                                        if re.match(r"(?:[\d]&)?[\w]+\s(?:&[\d])?[\w]+", token):
                                            ppp, copula = token.split(' ')
                                            post = re.match(r"([\d])&[\w]+", ppp)
                                            if post:
                                                offset += int(post.group(1))
                                                ppp = re.sub(r"[\d]&", '', ppp)
                                                original_length -= 2
                                                enjambed = True
                                            t.text = ppp.lower()
                                            t.startchar = start_char
                                            t.endchar = start_char + len(ppp) + offset
                                            if mode == 'index': self._cache.append(copy.copy(t))
                                            yield t
                                            pre = re.search(r"&(\d+?)", copula)
                                            if pre:
                                                start_char += int(pre.group(1))
                                                copula = re.sub(r"&\d+?", '', copula)
                                                original_length -= 2
                                                enjambed = True
                                            t.text = copula.lower()
                                            t.startchar = start_char + len(ppp) + 1
                                            t.endchar = start_char + len(ppp) + 1 + len(copula)
                                            if mode == 'index': self._cache.append(copy.copy(t))
                                            yield t
                                            start_char += original_length
                                            tpos += 1
                                            continue
                                        else:
                                            post = re.match(r"([\d])&[\w]+", token)
                                            if post:
                                                offset += int(post.group(1))
                                                token = re.sub(r"[\d]&", '', token)
                                                original_length -= 2
                                                enjambed = True
                                            else:
                                                offset = 0

                                        is_enclitic = False
                                        for enclitic in enclitics:
                                            if token.lower().endswith(enclitic):
                                                is_enclitic = True
                                                if enclitic == 'ne':
                                                    t.text = (token[:-len(enclitic)]).lower()
                                                    t.startchar = start_char
                                                    t.endchar = start_char + (len(token) - len(enclitic))
                                                    if mode == 'index': self._cache.append(copy.copy(t))
                                                    yield t
                                                    t.text = 'ne'
                                                    t.startchar = start_char + len(token[:-len(enclitic)]) + offset
                                                    t.endchar = start_char + len(token[:-len(enclitic)]) + len(enclitic) + offset
                                                    if mode == 'index': self._cache.append(copy.copy(t))
                                                    yield t
                                                elif enclitic == 'n':
                                                    t.text = (token[:-len(enclitic)] + 's').lower()
                                                    t.startchar = start_char
                                                    t.endchar = start_char + (len(token) + 1) - len(enclitic)
                                                    if mode == 'index': self._cache.append(copy.copy(t))
                                                    yield t
                                                    t.text = 'ne'
                                                    t.startchar = start_char + len(token[:-len(enclitic)]) + offset
                                                    t.endchar = start_char + len(token[:-len(enclitic)]) + len(enclitic) + offset
                                                    if mode == 'index': self._cache.append(copy.copy(t))
                                                    yield t
                                                elif enclitic == 'st':
                                                    if token.endswith('ust'):
                                                        t.text = (token[:-len(enclitic) + 1]).lower()
                                                        t.startchar = start_char
                                                        t.endchar = start_char + len(token[:-len(enclitic) + 1]) - len(enclitic)
                                                        if mode == 'index': self._cache.append(copy.copy(t))
                                                        yield t
                                                        t.text = 'est'
                                                        t.startchar = start_char + len(token[:-len(enclitic) + 1]) + offset
                                                        t.endchar = start_char + len(token[:-len(enclitic) + 1]) + len(enclitic) + offset
                                                        if mode == 'index': self._cache.append(copy.copy(t))
                                                        yield t
                                                    else:
                                                        t.text = (token[:-len(enclitic)]).lower()
                                                        t.startchar = start_char
                                                        t.endchar = start_char + len(token[:-len(enclitic)]) - len(enclitic)
                                                        if mode == 'index': self._cache.append(copy.copy(t))
                                                        yield t
                                                        t.text = 'est'
                                                        t.startchar = start_char + len(token[:-len(enclitic)]) + offset
                                                        t.endchar = start_char + len(token[:-len(enclitic)]) + len(enclitic) + offset
                                                        if mode == 'index': self._cache.append(copy.copy(t))
                                                        yield t
                                                elif enclitic == "'s":
                                                    t.text = token.lower() + 's'
                                                    t.startchar = start_char
                                                    t.endchar = start_char + len(token)
                                                    if mode == 'index': self._cache.append(copy.copy(t))
                                                    yield t
                                                    t.text = 'es'
                                                    t.startchar = start_char + len(token) + 1
                                                    t.endchar = start_char + len(token) + len(enclitic)
                                                    if mode == 'index': self._cache.append(copy.copy(t))
                                                    yield t
                                                else:
                                                    t.text = (token[:-len(enclitic)]).lower()
                                                    t.startchar = start_char
                                                    t.endchar = start_char + len(token[:-len(enclitic)])
                                                    if mode == 'index': self._cache.append(copy.copy(t))
                                                    yield t
                                                    t.text = enclitic
                                                    t.startchar = start_char + len(token[:-len(enclitic)]) + offset
                                                    t.endchar = start_char + len(token[:-len(enclitic)]) + len(enclitic) + offset
                                                    if mode == 'index': self._cache.append(copy.copy(t))
                                                    yield t
                                                break
                                    else:
                                        is_enclitic = False
                                        post = re.match(r"([\d])&[\w]+", token)
                                        if post:
                                            offset += int(post.group(1))
                                            token = re.sub(r"[\d]&", '', token)
                                            original_length -= 2
                                            enjambed = True
                                    if not is_enclitic:
                                        t.text = token
                                        if chars:
                                            t.startchar = start_char + ldiff
                                            t.endchar = start_char + original_length - rdiff + offset
                                        if mode == 'index':
                                            self._cache.append(copy.copy(t))
                                        yield t
                                        tpos += 1
                                    if enjambed:
                                        start_char += original_length + offset
                                    else:
                                        start_char += original_length
                            start_char += 1  # \n


class CachedPerseusJSONTokenizer(Tokenizer):
    def __init__(self, **kwargs):
        super(CachedPerseusJSONTokenizer, self).__init__()
        self.__dict__.update(**kwargs)
        self._cache = None
        self._docix = 0

    @property
    def cache(self):
        return copy.deepcopy(self._cache)

    def __call__(self, data, positions=True, chars=True,
                 keeporiginal=True, removestops=True, tokenize=True,
                 start_pos=0, start_char=0, mode='', **kwargs):
        if self._cache and kwargs.get('docix', None) == self._docix:
            yield from self.cache
        else:
            t = CylleneusToken(positions, chars, removestops=removestops, mode=mode, **kwargs)

            if t.mode == 'query':
                t.original = t.text = data
                yield t
                t.text = data.translate(jvmap)
                yield t
            elif t.mode == 'index':
                if not tokenize:
                    t.original = t.text = '\n'.join([el for el in flatten(data['text'])])
                    t.boost = 1.0
                    if positions:
                        t.pos = start_pos
                    if chars:
                        t.startchar = start_char
                        t.endchar = start_char + len(t.original)
                    yield t
                else:
                    self._cache = []
                    self._docix = kwargs.get('docix', 0)

                    word_tokenizer = PunktLatinCharsVars()
                    stopchars = str.maketrans('', '', string.punctuation + "“”—\n")

                    divs = { i: div.lower() for i, div in enumerate(data['meta'].split('-')) }

                    for path, value in nested_dict_iter(data['text']):
                        tokens = []

                        temp_tokens = word_tokenizer.word_tokenize(value)
                        if temp_tokens:
                            if temp_tokens[0].replace('j', 'i').replace('v', 'u') not in proper_names.proper_names:
                                temp_tokens[0] = temp_tokens[0].lower()

                            for ix, token in enumerate(temp_tokens):
                                ppp = compound.is_ppp(token)
                                if ppp and ix < len(temp_tokens) - 2:
                                    copula = compound.is_copula(temp_tokens[ix+2])  # whitespace
                                    if copula and ppp[1] == copula[2]:
                                        tense, mood, number, i = copula
                                        token = f"{token} {compound.copula[tense][mood][number][i]}"
                                        del temp_tokens[ix+1:ix+3]
                                        tokens.insert(ix, token)
                                    else:
                                        tokens.append(token)
                                else:
                                    tokens.append(token)

                        pos = 0
                        for token in tokens:
                            if token in (' ', '\n') or token in punctuation or token in stopchars:
                                pos -= 1
                            else:
                                pos += 2
                            meta = {
                                'meta': data['meta'].lower()
                            }
                            for i in range(len(divs)):
                                meta[divs[i]] = str(int(path[i]))
                            t.meta = meta
                            t.boost = 1.0
                            if keeporiginal:
                                t.original = token
                            t.stopped = False
                            if positions:
                                t.pos = start_pos + pos
                            original_length = len(token)

                            token = token.strip()
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
                            if not token:
                                start_char += original_length
                                continue

                            is_enclitic = False
                            if token not in exceptions:
                                if t.original in replacements:
                                    for subtoken in replacements[t.original]:
                                        t.text = subtoken.lower()
                                        t.startchar = start_char
                                        t.endchar = start_char + original_length
                                        if mode == 'index': self._cache.append(copy.copy(t))
                                        yield t
                                    start_char += original_length
                                    continue

                                if re.match(r"(?:\w+) (?:\w+)", token):
                                    ppp, copula = token.split(' ')
                                    t.text = ppp.lower()
                                    t.startchar = start_char
                                    t.endchar = start_char + len(ppp) + 1
                                    if mode == 'index': self._cache.append(copy.copy(t))
                                    yield t
                                    t.text = copula.lower()
                                    t.startchar = start_char + len(ppp)
                                    t.endchar = start_char + len(ppp) + len(copula)
                                    if mode == 'index': self._cache.append(copy.copy(t))
                                    yield t
                                    start_char += original_length
                                    continue

                                for enclitic in enclitics:
                                    if token.lower().endswith(enclitic):
                                        if enclitic == 'ne':
                                            t.text = (token[:-len(enclitic)]).lower()
                                            t.startchar = start_char
                                            t.endchar = start_char + (len(token) - len(enclitic))
                                            if mode == 'index': self._cache.append(copy.copy(t))
                                            yield t
                                            t.text = 'ne'
                                            t.startchar = start_char + len(token[:-len(enclitic)])
                                            t.endchar = start_char + len(token[:-len(enclitic)]) + len(enclitic)
                                            if mode == 'index': self._cache.append(copy.copy(t))
                                            yield t
                                        elif enclitic == 'n':
                                            t.text = (token[:-len(enclitic)] + 's').lower()
                                            t.startchar = start_char
                                            t.endchar = start_char + len(token) - len(enclitic)
                                            if mode == 'index': self._cache.append(copy.copy(t))
                                            yield t
                                            t.text = 'ne'
                                            t.startchar = start_char + len(token[:-len(enclitic)])
                                            t.endchar = start_char + len(token[:-len(enclitic)]) + len(enclitic)
                                            if mode == 'index': self._cache.append(copy.copy(t))
                                            yield t
                                        elif enclitic == 'st':
                                            if token.endswith('ust'):
                                                t.text = (token[:-len(enclitic)]).lower()
                                                t.startchar = start_char
                                                t.endchar = start_char + len(token[:-len(enclitic)]) - len(enclitic)
                                                if mode == 'index': self._cache.append(copy.copy(t))
                                                yield t
                                                t.text = 'est'
                                                t.startchar = start_char + len(token[:-len(enclitic)])
                                                t.endchar = start_char + len(token[:-len(enclitic)]) + len(enclitic)
                                                if mode == 'index': self._cache.append(copy.copy(t))
                                                yield t
                                            else:
                                                t.text = (token[:-len(enclitic)]).lower()
                                                t.startchar = start_char
                                                t.endchar = start_char + len(token[:-len(enclitic)]) - len(enclitic)
                                                if mode == 'index': self._cache.append(copy.copy(t))
                                                yield t
                                                t.text = 'est'
                                                t.startchar = start_char + len(token[:-len(enclitic)])
                                                t.endchar = start_char + len(token[:-len(enclitic)]) + len(enclitic)
                                                if mode == 'index': self._cache.append(copy.copy(t))
                                                yield t
                                        elif enclitic == "'s":
                                            t.text = token.lower() + 's'
                                            t.startchar = start_char
                                            t.endchar = start_char + len(token)
                                            if mode == 'index': self._cache.append(copy.copy(t))
                                            yield t
                                            t.text = 'es'
                                            t.startchar = start_char + len(token) + 1
                                            t.endchar = start_char + len(token) + len(enclitic)
                                            if mode == 'index': self._cache.append(copy.copy(t))
                                            yield t
                                        else:
                                            t.text = (token[:-len(enclitic)]).lower()
                                            t.startchar = start_char
                                            t.endchar = start_char + len(token[:-len(enclitic)])
                                            if mode == 'index': self._cache.append(copy.copy(t))
                                            yield t
                                            t.text = enclitic
                                            t.startchar = start_char + len(token[:-len(enclitic)])
                                            t.endchar = start_char + len(token[:-len(enclitic)]) + len(enclitic)
                                            if mode == 'index': self._cache.append(copy.copy(t))
                                            yield t
                                        is_enclitic = True
                                        break
                            if not is_enclitic:
                                t.text = token.lower()
                                if chars:
                                    t.startchar = start_char + ldiff
                                    t.endchar = start_char + original_length - rdiff  # - ndiff - rdiff
                                if mode == 'index': self._cache.append(copy.copy(t))
                                yield t
                            start_char += original_length
                        start_char += 1


class CachedPerseusTEITokenizer(Tokenizer):
    def __init__(self, **kwargs):
        super(CachedPerseusTEITokenizer, self).__init__()
        self.__dict__.update(**kwargs)
        self._cache = None
        self._docix = 0

    @property
    def cache(self):
        return copy.deepcopy(self._cache)

    def __call__(self, data, positions=True, chars=True,
                 keeporiginal=True, removestops=True, tokenize=True,
                 start_pos=0, start_char=0, mode='', **kwargs):
        if self._cache and kwargs.get('docix', None) == self._docix:
            yield from self.cache
        else:
            t = CylleneusToken(positions, chars, removestops=removestops, mode=mode, **kwargs)
            if t.mode == 'query':
                t.original = t.text = data.translate(jvmap)
                yield t
            else:
                if not tokenize:
                    text = '\n'.join([el for el in flatten(data['text'])])
                    t.original = t.text = text
                    t.boost = 1.0
                    if positions:
                        t.pos = start_pos
                    if chars:
                        t.startchar = start_char
                        t.endchar = start_char + len(text)
                    yield t
                else:
                    self._cache = []
                    self._docix = kwargs.get('docix', 0)

                    divs = { i: div for i, div in enumerate(data['meta'].split('-')) }

                    curr_divs = {}
                    for div in divs:
                        curr_divs[divs[div]] = 0

                    word_tokenizer = PunktLatinCharsVars()
                    stopchars = str.maketrans('', '', string.punctuation + "“”—\n")

                    for el in data['text'].find('.//{http://www.tei-c.org/ns/1.0}body').\
                            find(".//{http://www.tei-c.org/ns/1.0}div[@type='edition']").iter():
                        if el.tag == '{http://www.tei-c.org/ns/1.0}milestone':
                            curr_divs[el.get('unit')] = el.get('n')
                        elif el.tag == '{http://www.tei-c.org/ns/1.0}div' and el.get('type') == 'textpart':
                            curr_divs[el.get('subtype')] = el.get('n')
                            for passage in el:
                                speaker = None
                                for item in passage:
                                    if item.tag == '{http://www.tei-c.org/ns/1.0}l':
                                        curr_divs['verse'] = item.get('n')
                                        text = ' '.join([f"{l.text if l.text else ''}{l.tail if l.tail else ''}"
                                                         for l in item.iter()
                                                         if l.tag != '{http://www.tei-c.org/ns/1.0}del'
                                                         and l.tag != '{http://www.tei-c.org/ns/1.0}note']).translate(
                                            stopchars)
                                    elif item.tag == '{http://www.tei-c.org/ns/1.0}seg':
                                        curr_divs[passage.get('type')] = item.get('n')
                                        text = ' '.join([f"{l.text if l.text else ''}{l.tail if l.tail else ''}"
                                                         for l in item.iter()
                                                         if l.tag != '{http://www.tei-c.org/ns/1.0}del'
                                                         and l.tag != '{http://www.tei-c.org/ns/1.0}note']).translate(
                                            stopchars)
                                    elif item.tag == '{http://www.tei-c.org/ns/1.0}speaker':
                                        speaker = item.text
                                        continue
                                    elif item.tag == '{http://www.tei-c.org/ns/1.0}p':
                                        text = ' '.join([f"{l.text if l.text else ''}{l.tail if l.tail else ''}"
                                                         for l in item.iter()
                                                         if l.tag != '{http://www.tei-c.org/ns/1.0}del'
                                                         and l.tag != '{http://www.tei-c.org/ns/1.0}note']).translate(
                                            stopchars)
                                    else:
                                        continue
                                    tokens = []
                                    temp_tokens = word_tokenizer.word_tokenize(text)
                                    if temp_tokens:
                                        if temp_tokens[0].translate(jvmap) not in proper_names.proper_names:
                                            temp_tokens[0] = temp_tokens[0].lower()

                                        for ix, token in enumerate(temp_tokens):
                                            if token == ' ':
                                                continue
                                            ppp = compound.is_ppp(token)
                                            if ppp and ix < len(temp_tokens) - 2:
                                                copula = compound.is_copula(temp_tokens[ix+2])  # whitespace
                                                if copula and ppp[1] == copula[2]:
                                                    tense, mood, number, i = copula
                                                    token = f"{token} {compound.copula[tense][mood][number][i]}"
                                                    del temp_tokens[ix+1:ix+3]
                                                    tokens.insert(ix, token)
                                                else:
                                                    tokens.append(token)
                                            else:
                                                tokens.append(token)

                                    for pos, token in enumerate(tokens):
                                        meta = {}
                                        for div in curr_divs:
                                            meta[div] = curr_divs[div]
                                        if speaker:
                                            meta['speaker'] = speaker
                                        t.meta = meta

                                        t.boost = 1.0
                                        if keeporiginal:
                                            t.original = token
                                        t.stopped = False
                                        if positions:
                                            t.pos = start_pos + pos
                                        original_length = len(token)

                                        token = token.strip()
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
                                        if not token:
                                            start_char += original_length
                                            continue

                                        is_enclitic = False
                                        if token not in exceptions:
                                            if t.original in replacements:
                                                for subtoken in replacements[t.original]:
                                                    t.text = subtoken.lower()
                                                    t.startchar = start_char
                                                    t.endchar = start_char + original_length
                                                    if mode == 'index': self._cache.append(copy.copy(t))
                                                    yield t
                                                start_char += original_length
                                                continue

                                            if re.match(r"(?:\w+) (?:\w+)", token):
                                                ppp, copula = token.split(' ')
                                                t.text = ppp.lower()
                                                t.startchar = start_char
                                                t.endchar = start_char + len(ppp) + 1
                                                if mode == 'index': self._cache.append(copy.copy(t))
                                                yield t
                                                t.text = copula.lower()
                                                t.startchar = start_char + len(ppp)
                                                t.endchar = start_char + len(ppp) + len(copula)
                                                if mode == 'index': self._cache.append(copy.copy(t))
                                                yield t
                                                start_char += original_length
                                                continue

                                            for enclitic in enclitics:
                                                if token.lower().endswith(enclitic):
                                                    if enclitic == 'ne':
                                                        t.text = (token[:-len(enclitic)]).lower()
                                                        t.startchar = start_char
                                                        t.endchar = start_char + (len(token) - len(enclitic))
                                                        if mode == 'index': self._cache.append(copy.copy(t))
                                                        yield t
                                                        t.text = 'ne'
                                                        t.startchar = start_char + len(token[:-len(enclitic)])
                                                        t.endchar = start_char + len(token[:-len(enclitic)]) + len(enclitic)
                                                        if mode == 'index': self._cache.append(copy.copy(t))
                                                        yield t
                                                    elif enclitic == 'n':
                                                        t.text = (token[:-len(enclitic)] + 's').lower()
                                                        t.startchar = start_char
                                                        t.endchar = start_char + len(token) - len(enclitic)
                                                        if mode == 'index': self._cache.append(copy.copy(t))
                                                        yield t
                                                        t.text = 'ne'
                                                        t.startchar = start_char + len(token[:-len(enclitic)])
                                                        t.endchar = start_char + len(token[:-len(enclitic)]) + len(enclitic)
                                                        if mode == 'index': self._cache.append(copy.copy(t))
                                                        yield t
                                                    elif enclitic == 'st':
                                                        if token.endswith('ust'):
                                                            t.text = (token[:-len(enclitic)]).lower()
                                                            t.startchar = start_char
                                                            t.endchar = start_char + len(token[:-len(enclitic)]) - len(enclitic)
                                                            if mode == 'index': self._cache.append(copy.copy(t))
                                                            yield t
                                                            t.text = 'est'
                                                            t.startchar = start_char + len(token[:-len(enclitic)])
                                                            t.endchar = start_char + len(token[:-len(enclitic)]) + len(enclitic)
                                                            if mode == 'index': self._cache.append(copy.copy(t))
                                                            yield t
                                                        else:
                                                            t.text = (token[:-len(enclitic)]).lower()
                                                            t.startchar = start_char
                                                            t.endchar = start_char + len(token[:-len(enclitic)]) - len(enclitic)
                                                            if mode == 'index': self._cache.append(copy.copy(t))
                                                            yield t
                                                            t.text = 'est'
                                                            t.startchar = start_char + len(token[:-len(enclitic)])
                                                            t.endchar = start_char + len(token[:-len(enclitic)]) + len(enclitic)
                                                            if mode == 'index': self._cache.append(copy.copy(t))
                                                            yield t
                                                    elif enclitic == "'s":
                                                        t.text = token.lower() + 's'
                                                        t.startchar = start_char
                                                        t.endchar = start_char + len(token)
                                                        if mode == 'index': self._cache.append(copy.copy(t))
                                                        yield t
                                                        t.text = 'es'
                                                        t.startchar = start_char + len(token) + 1
                                                        t.endchar = start_char + len(token) + len(enclitic)
                                                        if mode == 'index': self._cache.append(copy.copy(t))
                                                        yield t
                                                    else:
                                                        t.text = (token[:-len(enclitic)]).lower()
                                                        t.startchar = start_char
                                                        t.endchar = start_char + len(token[:-len(enclitic)])
                                                        if mode == 'index': self._cache.append(copy.copy(t))
                                                        yield t
                                                        t.text = enclitic
                                                        t.startchar = start_char + len(token[:-len(enclitic)])
                                                        t.endchar = start_char + len(token[:-len(enclitic)]) + len(enclitic)
                                                        if mode == 'index': self._cache.append(copy.copy(t))
                                                        yield t
                                                    is_enclitic = True
                                                    break
                                        if not is_enclitic:
                                            t.text = token.lower()
                                            if chars:
                                                t.startchar = start_char + ldiff
                                                t.endchar = start_char + original_length - rdiff  # - ndiff - rdiff
                                            if mode == 'index': self._cache.append(copy.copy(t))
                                            yield t
                                        start_char += original_length + 1


class CachedLASLATokenizer(Tokenizer):
    def __init__(self, **kwargs):
        super(CachedLASLATokenizer, self).__init__()
        self.__dict__.update(**kwargs)
        self._cache = None
        self._docix = 0

    @property
    def cache(self):
        return copy.deepcopy(self._cache)

    def __call__(self, data: dict, positions=False, chars=False,
                 keeporiginal=True, removestops=True, tokenize=True,
                 start_pos=0, start_char=0, mode='', **kwargs):
        if self._cache and kwargs.get('docix', None) == self._docix:
            yield from self.cache
        else:
            t = engine.analysis.acore.CylleneusToken(positions, chars, removestops=removestops, mode=mode, **kwargs)

            if t.mode == 'query':
                t.original = t.text = data.translate(jvmap)
                yield t
            else:
                if not tokenize:
                    t.original = t.text = '\n'.join([el for el in data['text']])
                    t.boost = 1.0
                    if positions:
                        t.pos = start_pos
                    if chars:
                        t.startchar = start_char
                        t.endchar = start_char + len(data['text'])
                    yield t
                else:
                    self._cache = []
                    self._docix = kwargs.get('docix', 0)

                    punctmap = str.maketrans('', '', '[{(<>)}]')
                    added = re.compile(r"(\s?[<(][\w .]+[>)]\s?)")

                    t.boost = 1.0
                    t.pos = t.startchar = t.endchar = 0

                    sect_sent = 1  # sentence count within passage
                    sent_id = '0001'
                    sect_pos = 1   # word pos within passage
                    sent_pos = 1    # word pos within sentence
                    current_refs = tuple(['0'] * len(data['meta']))
                    nflag = None
                    morpho_buffer = None
                    for pos, line in enumerate(data['text']):
                        t.pos = pos
                        parsed = parse_bpn(line)

                        if not parsed:
                            continue

                        if int(parsed['sent_id']) > int(sent_id):
                            sent_pos = 1
                            sent_id = parsed['sent_id']
                            if tuple(parsed['refs'].split(',')) > current_refs:
                                sect_sent = 1
                            else:
                                sect_sent += 1

                        if keeporiginal:
                            if added.search(parsed['form']):
                                t.original = added.sub('', parsed['form'])
                            else:
                                t.original = parsed['form']
                        t.stopped = False

                        if parsed['form_code'] == '&' or parsed['form_code'] == '+':
                            if parsed['lemma'] != '#':
                                if parsed['lemma'] == '_SVM':
                                    t.text = parsed['form'].translate(punctmap)
                                    t.morpho = None
                                    t.lemma = parsed['lemma']
                                    t.lemma_n = parsed['lemma_n']
                                    t.original = added.sub('', parsed['form'])
                                else:
                                    form = parsed['form']
                                    t.morpho = parsed['morpho']

                                    if ' ' in form:
                                        t.original = added.sub('', form)
                                        text = form.translate(punctmap)
                                    else:
                                        t.original = form
                                        text = form
                                    t.text = text.translate(punctmap)
                                    t.lemma = parsed['lemma']
                                    t.lemma_n = parsed['lemma_n']
                                    if added.search(parsed['form']):
                                        t.original = added.sub('', parsed['form'])
                                    nflag = False
                            else:
                                # could be a Greek form, do we index it?
                                sent_pos += 1
                                sect_pos += 1
                                continue
                        elif parsed['form_code'] == '@':  # combined forms
                            if parsed['lemma'] != '#':
                                t.lemma = parsed['lemma']
                                t.lemma_n = parsed['lemma_n']
                                t.text = parsed['form'].translate(punctmap)
                                t.morpho = parsed['morpho']
                                if nflag:
                                    sect_pos -= 1
                                    sent_pos -= 1
                                else:
                                    nflag = True
                            else:
                                sent_pos += 1
                                sect_pos += 1
                                continue
                        elif parsed['form_code'] == '=':  # que
                            t.text = parsed['form'].translate(punctmap)
                            t.lemma = parsed['lemma']
                            t.lemma_n = parsed['lemma_n']
                            t.morpho = parsed['morpho']
                            sent_pos -= 1
                            sect_pos -= 1
                            nflag = False
                        meta = {
                            'meta': data['meta'].lower()
                        }
                        tags = data['meta'].split('-')
                        if len(tags) > 2 and 'line' in tags:
                            tags.pop(tags.index('line'))
                        divs = {i: div.lower() for i, div in enumerate(tags)}
                        refs = tuple(parsed['refs'].strip().split(','))
                        for i in range(len(divs)):
                            meta[divs[i]] = refs[i]
                        _meta = meta.copy()
                        if tuple(ref for ref in _meta.values()) > current_refs:
                            sect_pos = 1
                        else:
                            sect_pos += 1

                        current_refs = tuple(ref for ref in refs)
                        meta['sent_id'] = parsed['sent_id']
                        meta['sect_sent'] = str(sect_sent)
                        meta['sect_pos'] = str(sect_pos)
                        meta['sent_pos'] = str(sent_pos)
                        t.meta = meta
                        t.morphosyntax = parsed['subord']

                        t.startchar = start_char
                        t.endchar = start_char + len(t.original)
                        yield t
                        sent_pos += 1
                        start_char += len(t.original) + 1


# class CachedPROIELXmlTokenizer(Tokenizer):
#     def __init__(self, **kwargs):
#         super(CachedPROIELXmlTokenizer, self).__init__()
#         self.__dict__.update(**kwargs)
#         self._cache = None
#         self._docix = 0
#
#     @property
#     def cache(self):
#         return copy.deepcopy(self._cache)
#
#     def __call__(self, value: bytes, positions=True, chars=True,
#                  keeporiginal=True, removestops=True, tokenize=True,
#                  start_pos=0, start_char=0, mode='', **kwargs):
#         if self._cache and kwargs.get('docix', None) == self._docix:
#             yield from self.cache
#         else:
#             self._cache = []
#             self._docix = kwargs.get('docix', 0)
#
#             parser = et.XMLParser(encoding='utf-8')
#             tree = et.XML(value, parser=parser)
#
#             t = CylleneusToken(positions, chars, removestops=removestops, mode=mode, **kwargs)
#             if not tokenize:
#                 t.original = ''
#                 for token in tree.findall('.//token'):
#                     form = token.get('form')
#                     if not form:
#                         continue
#                     after = token.get('presentation-after')
#                     before = token.get('presentation-before')
#                     t.original += f"{before if before else ''}{form}{after if after else ''}"
#                 t.text = t.original
#                 t.boost = 1.0
#                 if positions:
#                     t.pos = start_pos
#                 if chars:
#                     t.startchar = start_char
#                     t.endchar = start_char + len(t.original)
#                 yield t
#             else:
#                 for pos, token in enumerate(tree.findall('.//token')):
#                     form = token.get('form')
#                     if not form:
#                         continue
#                     else:
#                         form = form.replace(' ', ' ').replace(' ', ' ')
#                         form = re.sub(r"\.([^ ]|^$)", r'. \1', form)
#                     after = token.get('presentation-after')
#                     before = token.get('presentation-before')
#                     if not after:
#                         after = ''
#                     if not before:
#                         before = ''
#                     t.lemma = token.get('lemma')
#                     t.morpho = from_proiel(token.get('part-of-speech'), token.get('morphology'))
#
#                     t.boost = 1.0
#
#                     if keeporiginal:
#                         t.original = f"{before}{form}{after}"
#                     t.stopped = False
#                     if positions:
#                         t.pos = start_pos + pos
#
#                     if form in editorial:
#                         form = editorial[form]
#
#                     if re.match(r"(?:\w+) (?:\w+)", form):
#                         if before: start_char += len(before)
#                         subforms = form.split(' ')
#                         for ix, subform in enumerate(subforms):
#                             if subform in replacements:
#                                 original_len = len(subform)
#                                 for subsubform in replacements[subform]:
#                                     if ix+1 < len(subforms) and (subforms[ix+1].endswith('iis') or subforms[ix+1].endswith('ibus')):
#                                         t.text = re.sub(r"as$", "is", subsubform)
#                                     else:
#                                         t.text = subsubform
#                                     if chars:
#                                         t.startchar = start_char
#                                         t.endchar = start_char + original_len
#                                         if mode == 'index': self._cache.append(copy.copy(t))
#                                     yield t
#                                     start_char += original_len
#                             else:
#                                 original_len = len(subform)
#                                 num = roman_to_arabic(subform)
#                                 if num:
#                                     subform = str(num)
#                                 t.text = subform
#                                 if chars:
#                                     t.startchar = start_char
#                                     t.endchar = start_char + original_len
#                                 if mode == 'index': self._cache.append(copy.copy(t))
#                                 yield t
#                                 start_char += len(subform)
#                         if after: start_char += len(after)
#                         continue
#
#                     if form in replacements:
#                         if before: start_char += len(before)
#                         for subtoken in replacements[form]:
#                             t.text = subtoken
#                             if chars:
#                                 t.startchar = start_char
#                                 t.endchar = start_char + len(subtoken)
#                             if mode == 'index': self._cache.append(copy.copy(t))
#                             yield t
#                             start_char += len(subtoken)
#                         start_char += len(after)
#                     else:
#                         original_len = len(form)
#                         num = roman_to_arabic(form)
#                         if num:
#                             form = str(num)
#                         t.text = form
#                         if chars:
#                             t.startchar = start_char + len(before)
#                             t.endchar = start_char + len(before) + original_len
#                         if mode == 'index': self._cache.append(copy.copy(t))
#                         yield t
#                     start_char += len(before) + original_len + len(after)
