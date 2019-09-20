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
from collections import deque

import engine.analysis
from engine.analysis.acore import Composable, CylleneusToken
from lang.latin import compound, jvmap, proper_names, punctuation, roman_to_arabic, sent_tokenizer, word_tokenizer, \
    replacements, editorial, exceptions, enclitics, PunktLatinCharsVars
from lxml.etree import ElementTree
from utils import flatten, stringify, nested_dict_iter
from whoosh.compat import text_type, u
from whoosh.util.text import rcompile

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


class CachedPlainTextTokenizer(Tokenizer):
    def __init__(self, **kwargs):
        super(CachedPlainTextTokenizer, self).__init__()
        self.__dict__.update(**kwargs)
        self._cache = None
        self._docix = None

    @property
    def cache(self):
        return copy.deepcopy(self._cache)

    def __call__(self, value: str, positions=True, chars=True,
                 keeporiginal=True, removestops=True, tokenize=True,
                 start_pos=0, start_char=0, mode='', **kwargs):
        if kwargs.get('docix', None) == self._docix and self._cache:
            yield from self.cache
        else:
            t = CylleneusToken(positions, chars, removestops=removestops, mode=mode, **kwargs)

            if t.mode == 'query':
                t.original = t.text = value.translate(jvmap)
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
                    self._docix = kwargs.get('docix', None)

                    sents = sent_tokenizer.tokenize(value)
                    stopchars = str.maketrans('', '', string.punctuation.replace('-', ''))

                    tokens = []
                    sent_id = 0
                    for i, sent in enumerate(sents):
                        sent_id += i
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
                        sent_pos = pos

                        t.meta = {
                            'sent_id': sent_id,
                            'sent_pos': sent_pos
                        }
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
                                    if mode == 'index': self._cache.append(copy.deepcopy(t))
                                    yield t
                                start_char += original_length + 1
                                continue

                            if re.match(r"(?:\w+) (?:\w+)", token):
                                ppp, copula = token.split(' ')
                                t.text = ppp.lower()
                                t.startchar = start_char
                                t.endchar = start_char + len(ppp)
                                if mode == 'index': self._cache.append(copy.deepcopy(t))
                                yield t
                                t.text = copula.lower()
                                t.startchar = start_char + len(ppp) + 1
                                t.endchar = start_char + len(ppp) + 1 + len(copula)
                                if mode == 'index': self._cache.append(copy.deepcopy(t))
                                yield t
                                start_char += original_length + 1
                                continue

                            for enclitic in enclitics:
                                if token.lower().endswith(enclitic):
                                    if enclitic == 'ne':
                                        t.text = (token[:-len(enclitic)]).lower()
                                        t.startchar = start_char
                                        t.endchar = start_char + (len(token) - len(enclitic))
                                        if mode == 'index': self._cache.append(copy.deepcopy(t))
                                        yield t
                                        t.text = 'ne'
                                        t.startchar = start_char + len(token[:-len(enclitic)])
                                        t.endchar = start_char + len(token[:-len(enclitic)]) + len(enclitic)
                                        if mode == 'index': self._cache.append(copy.deepcopy(t))
                                        yield t
                                    elif enclitic == 'n':
                                        t.text = (token[:-len(enclitic)] + 's').lower()
                                        t.startchar = start_char
                                        t.endchar = start_char + (len(token) + 1) - len(enclitic)
                                        if mode == 'index': self._cache.append(copy.deepcopy(t))
                                        yield t
                                        t.text = 'ne'
                                        t.startchar = start_char + len(token[:-len(enclitic)])
                                        t.endchar = start_char + len(token[:-len(enclitic)]) + len(enclitic)
                                        if mode == 'index': self._cache.append(copy.deepcopy(t))
                                        yield t
                                    elif enclitic == 'st':
                                        if token.endswith('ust'):
                                            t.text = (token[:-len(enclitic) + 1]).lower()
                                            t.startchar = start_char
                                            t.endchar = start_char + len(token[:-len(enclitic) + 1]) - len(enclitic)
                                            if mode == 'index': self._cache.append(copy.deepcopy(t))
                                            yield t
                                            t.text = 'est'
                                            t.startchar = start_char + len(token[:-len(enclitic) + 1])
                                            t.endchar = start_char + len(token[:-len(enclitic) + 1]) + len(enclitic)
                                            if mode == 'index': self._cache.append(copy.deepcopy(t))
                                            yield t
                                        else:
                                            t.text = (token[:-len(enclitic)]).lower()
                                            t.startchar = start_char
                                            t.endchar = start_char + len(token[:-len(enclitic)]) - len(enclitic)
                                            if mode == 'index': self._cache.append(copy.deepcopy(t))
                                            yield t
                                            t.text = 'est'
                                            t.startchar = start_char + len(token[:-len(enclitic) + 1])
                                            t.endchar = start_char + len(token[:-len(enclitic) + 1]) + len(enclitic)
                                            if mode == 'index': self._cache.append(copy.deepcopy(t))
                                            yield t
                                    elif enclitic == "'s":
                                        t.text = token + 's'
                                        t.startchar = start_char
                                        t.endchar = start_char + len(token)
                                        if mode == 'index': self._cache.append(copy.deepcopy(t))
                                        yield t
                                        t.text = 'es'
                                        t.startchar = start_char + len(token) + 1
                                        t.endchar = start_char + len(token) + len(enclitic)
                                        if mode == 'index': self._cache.append(copy.deepcopy(t))
                                        yield t
                                    else:
                                        t.text = (token[:-len(enclitic)])
                                        t.startchar = start_char
                                        t.endchar = start_char + len(token[:-len(enclitic)])
                                        if mode == 'index': self._cache.append(copy.deepcopy(t))
                                        yield t
                                        t.text = enclitic
                                        t.startchar = start_char + len(token[:-len(enclitic)])
                                        t.endchar = start_char + len(token[:-len(enclitic)]) + len(enclitic)
                                        if mode == 'index': self._cache.append(copy.deepcopy(t))
                                        yield t
                                    is_enclitic = True
                                    break
                        if not is_enclitic:
                            t.text = token
                            if chars:
                                t.startchar = start_char + ldiff
                                t.endchar = start_char + original_length - rdiff  # - ndiff - rdiff
                            if mode == 'index': self._cache.append(copy.deepcopy(t))
                            yield t
                        start_char += original_length + 1


class CachedPerseusJSONTokenizer(Tokenizer):
    def __init__(self, **kwargs):
        super(CachedPerseusJSONTokenizer, self).__init__()
        self.__dict__.update(**kwargs)
        self._cache = None
        self._docix = None

    @property
    def cache(self):
        return copy.deepcopy(self._cache)

    def __call__(self, value, positions=True, chars=True,
                 keeporiginal=True, removestops=True, tokenize=True,
                 start_pos=0, start_char=0, mode='', **kwargs):
        if kwargs.get('docix', None) == self._docix and self._cache:
            yield from self.cache
        else:
            t = CylleneusToken(positions, chars, removestops=removestops, mode=mode, **kwargs)

            if t.mode == 'query':
                t.original = t.text = value.translate(jvmap)
                yield t
            elif t.mode == 'index':
                if not tokenize:
                    t.original = t.text = '\n'.join([el for el in flatten(value['text'])])
                    t.boost = 1.0
                    if positions:
                        t.pos = start_pos
                    if chars:
                        t.startchar = start_char
                        t.endchar = start_char + len(t.original)
                    yield t
                else:
                    self._cache = []
                    self._docix = kwargs.get('docix', None)

                    tokenizer = PunktLatinCharsVars()
                    stopchars = str.maketrans('', '', string.punctuation + "“”—\n")

                    divs = { i: div.lower() for i, div in enumerate(value['meta'].split('-')) }

                    sect_sent = 0
                    prev_sect = 0
                    sect_pos = 0
                    for i, (path, text) in enumerate(nested_dict_iter(value['text'])):
                        sent_id = i
                        if len(path) >= 2 and int(path[-2]) > prev_sect:
                            sect_sent = 0
                            sect_pos = 0
                            prev_sect = int(path[-2])
                        tokens = []

                        temp_tokens = tokenizer.word_tokenize(text)
                        if temp_tokens:
                            if temp_tokens[0].replace('j', 'i').replace('v', 'u') not in proper_names.proper_names:
                                temp_tokens[0] = temp_tokens[0]

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
                        sent_pos = 0
                        for token in tokens:
                            meta = {
                                'meta': value['meta'].lower()
                            }
                            for i in range(len(divs)):
                                meta[divs[i]] = str(int(path[i]) + 1)

                            t.boost = 1.0
                            if keeporiginal:
                                t.original = token
                            t.stopped = False

                            if token in (' ', '\n') or token in punctuation or token in stopchars:
                                pos -= 1
                            else:
                                pos += 2
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

                            meta['sect_sent'] = sect_sent
                            meta['sect_pos'] = sect_pos
                            meta['sent_id'] = sent_id
                            meta['sent_pos'] = sent_pos
                            t.meta = meta

                            is_enclitic = False
                            if token not in exceptions:
                                if t.original in replacements:
                                    for subtoken in replacements[t.original]:
                                        t.text = subtoken
                                        t.startchar = start_char
                                        t.endchar = start_char + original_length
                                        if mode == 'index': self._cache.append(copy.deepcopy(t))
                                        yield t
                                    start_char += original_length
                                    continue

                                if re.match(r"(?:\w+) (?:\w+)", token):
                                    ppp, copula = token.split(' ')
                                    t.text = ppp
                                    t.startchar = start_char
                                    t.endchar = start_char + len(ppp) + 1
                                    if mode == 'index': self._cache.append(copy.deepcopy(t))
                                    yield t
                                    t.text = copula
                                    t.startchar = start_char + len(ppp)
                                    t.endchar = start_char + len(ppp) + len(copula)
                                    if mode == 'index': self._cache.append(copy.deepcopy(t))
                                    yield t
                                    start_char += original_length
                                    continue

                                for enclitic in enclitics:
                                    if token.endswith(enclitic):
                                        if enclitic == 'ne':
                                            t.text = (token[:-len(enclitic)])
                                            t.startchar = start_char
                                            t.endchar = start_char + (len(token) - len(enclitic))
                                            if mode == 'index': self._cache.append(copy.deepcopy(t))
                                            yield t
                                            t.text = 'ne'
                                            t.startchar = start_char + len(token[:-len(enclitic)])
                                            t.endchar = start_char + len(token[:-len(enclitic)]) + len(enclitic)
                                            if mode == 'index': self._cache.append(copy.deepcopy(t))
                                            yield t
                                        elif enclitic == 'n':
                                            t.text = (token[:-len(enclitic)] + 's')
                                            t.startchar = start_char
                                            t.endchar = start_char + len(token) - len(enclitic)
                                            if mode == 'index': self._cache.append(copy.deepcopy(t))
                                            yield t
                                            t.text = 'ne'
                                            t.startchar = start_char + len(token[:-len(enclitic)])
                                            t.endchar = start_char + len(token[:-len(enclitic)]) + len(enclitic)
                                            if mode == 'index': self._cache.append(copy.deepcopy(t))
                                            yield t
                                        elif enclitic == 'st':
                                            if token.endswith('ust'):
                                                t.text = (token[:-len(enclitic)])
                                                t.startchar = start_char
                                                t.endchar = start_char + len(token[:-len(enclitic)]) - len(enclitic)
                                                if mode == 'index': self._cache.append(copy.deepcopy(t))
                                                yield t
                                                t.text = 'est'
                                                t.startchar = start_char + len(token[:-len(enclitic)])
                                                t.endchar = start_char + len(token[:-len(enclitic)]) + len(enclitic)
                                                if mode == 'index': self._cache.append(copy.deepcopy(t))
                                                yield t
                                            else:
                                                t.text = (token[:-len(enclitic)])
                                                t.startchar = start_char
                                                t.endchar = start_char + len(token[:-len(enclitic)]) - len(enclitic)
                                                if mode == 'index': self._cache.append(copy.deepcopy(t))
                                                yield t
                                                t.text = 'est'
                                                t.startchar = start_char + len(token[:-len(enclitic)])
                                                t.endchar = start_char + len(token[:-len(enclitic)]) + len(enclitic)
                                                if mode == 'index': self._cache.append(copy.deepcopy(t))
                                                yield t
                                        elif enclitic == "'s":
                                            t.text = token + 's'
                                            t.startchar = start_char
                                            t.endchar = start_char + len(token)
                                            if mode == 'index': self._cache.append(copy.deepcopy(t))
                                            yield t
                                            t.text = 'es'
                                            t.startchar = start_char + len(token) + 1
                                            t.endchar = start_char + len(token) + len(enclitic)
                                            if mode == 'index': self._cache.append(copy.deepcopy(t))
                                            yield t
                                        else:
                                            t.text = (token[:-len(enclitic)])
                                            t.startchar = start_char
                                            t.endchar = start_char + len(token[:-len(enclitic)])
                                            if mode == 'index': self._cache.append(copy.deepcopy(t))
                                            yield t
                                            t.text = enclitic
                                            t.startchar = start_char + len(token[:-len(enclitic)])
                                            t.endchar = start_char + len(token[:-len(enclitic)]) + len(enclitic)
                                            if mode == 'index': self._cache.append(copy.deepcopy(t))
                                            yield t
                                        is_enclitic = True
                                        break
                            if not is_enclitic:
                                t.text = token
                                if chars:
                                    t.startchar = start_char + ldiff
                                    t.endchar = start_char + original_length - rdiff  # - ndiff - rdiff
                                if mode == 'index':
                                    self._cache.append(copy.deepcopy(t))
                                yield t
                            start_char += original_length
                            sent_pos += 1
                            sect_pos += 1
                        start_char += 1


class CachedPerseusXMLTokenizer(Tokenizer):
    def __init__(self, **kwargs):
        super(CachedPerseusXMLTokenizer, self).__init__()
        self.__dict__.update(**kwargs)
        self._cache = None
        self._docix = None

    @property
    def cache(self):
        return copy.deepcopy(self._cache)

    def __call__(self, value, positions=True, chars=True,
                 keeporiginal=True, removestops=True, tokenize=True,
                 start_pos=0, start_char=0, mode='', **kwargs):
        if kwargs.get('docix', None) == self._docix and self._cache:
            yield from self.cache
        else:
            t = CylleneusToken(positions, chars, removestops=removestops, mode=mode, **kwargs)
            if t.mode == 'query':
                t.original = t.text = value.translate(jvmap)
                yield t
            else:
                if not tokenize:
                    text = '\n'.join([el for el in flatten(value['text'])])
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
                    self._docix = kwargs.get('docix', None)

                    tokenizer = PunktLatinCharsVars()
                    stopchars = str.maketrans('', '', string.punctuation)

                    doc = value['text']
                    refs = doc.find(
                        ".//{http://www.tei-c.org/ns/1.0}encodingDesc"
                    ).find(
                        ".//{http://www.tei-c.org/ns/1.0}refsDecl[@n='CTS']"
                    )
                    divs = list(reversed([
                        cref.get('n')
                        for cref in refs.findall(".//{http://www.tei-c.org/ns/1.0}cRefPattern")
                    ]))
                    sentences = doc.xpath("/tei:TEI/tei:text/tei:body/tei:div" + ("/tei:div" * len(divs)),
                                          namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})

                    if len(sentences) == 0:
                        sentences = doc.xpath("/tei:TEI/tei:text/tei:body/tei:div" + ("/tei:div" * (len(divs)-1)) +
                                              "/tei:l",
                                              namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})

                    for i, sentence in enumerate(sentences):
                        meta = {
                            'meta': '-'.join(divs),
                            divs[-1]: sentence.get('n'),
                            'sent_id': i
                        }

                        el = sentence
                        j = 0
                        while(el.getparent() is not None and el.getparent().get('type', None) == 'textpart'):
                            meta[divs[j]] = el.getparent().get('n')
                            el = el.getparent()
                            j += 1

                        text = stringify(sentence)

                        tokens = []
                        temp_tokens = tokenizer.word_tokenize(text)

                        if temp_tokens:
                            if temp_tokens[0].replace('j', 'i').replace('v', 'u') not in proper_names.proper_names:
                                temp_tokens[0] = temp_tokens[0]

                            for ix, token in enumerate(temp_tokens):
                                ppp = compound.is_ppp(token)
                                if ppp and ix < len(temp_tokens) - 2:
                                    copula = compound.is_copula(temp_tokens[ix + 2])  # whitespace
                                    if copula and ppp[1] == copula[2]:
                                        tense, mood, number, i = copula
                                        token = f"{token} {compound.copula[tense][mood][number][i]}"
                                        del temp_tokens[ix + 1:ix + 3]
                                        tokens.insert(ix, token)
                                    else:
                                        tokens.append(token)
                                else:
                                    tokens.append(token)

                        pos = 0
                        for token in tokens:
                            meta['sent_pos'] = pos

                            t.boost = 1.0
                            if keeporiginal:
                                t.original = token
                            t.stopped = False

                            if positions:
                                t.pos = start_pos + pos
                            if token == ' ' or token in punctuation or token in stopchars:
                                pos += 1
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

                            t.meta = copy.deepcopy(meta)

                            is_enclitic = False
                            if token not in exceptions:
                                if t.original in replacements:
                                    for subtoken in replacements[t.original]:
                                        t.text = subtoken
                                        t.startchar = start_char
                                        t.endchar = start_char + original_length
                                        if mode == 'index':
                                            self._cache.append(copy.deepcopy(t))
                                        yield t
                                    start_char += original_length
                                    continue

                                if re.match(r"(?:\w+) (?:\w+)", token):
                                    ppp, copula = token.split(' ')
                                    t.text = ppp
                                    t.startchar = start_char
                                    t.endchar = start_char + len(ppp) + 1
                                    if mode == 'index':
                                        self._cache.append(copy.deepcopy(t))
                                    yield t
                                    t.text = copula
                                    t.startchar = start_char + len(ppp)
                                    t.endchar = start_char + len(ppp) + len(copula)
                                    if mode == 'index':
                                        self._cache.append(copy.deepcopy(t))
                                    yield t
                                    start_char += original_length
                                    continue

                                for enclitic in enclitics:
                                    if token.endswith(enclitic):
                                        if enclitic == 'ne':
                                            t.text = (token[:-len(enclitic)])
                                            t.startchar = start_char
                                            t.endchar = start_char + (len(token) - len(enclitic))
                                            if mode == 'index':
                                                self._cache.append(copy.deepcopy(t))
                                            yield t
                                            t.text = 'ne'
                                            t.startchar = start_char + len(token[:-len(enclitic)])
                                            t.endchar = start_char + len(token[:-len(enclitic)]) + len(enclitic)
                                            if mode == 'index':
                                                self._cache.append(copy.deepcopy(t))
                                            yield t
                                        elif enclitic == 'n':
                                            t.text = (token[:-len(enclitic)] + 's')
                                            t.startchar = start_char
                                            t.endchar = start_char + len(token) - len(enclitic)
                                            if mode == 'index':
                                                self._cache.append(copy.deepcopy(t))
                                            yield t
                                            t.text = 'ne'
                                            t.startchar = start_char + len(token[:-len(enclitic)])
                                            t.endchar = start_char + len(token[:-len(enclitic)]) + len(enclitic)
                                            if mode == 'index':
                                                self._cache.append(copy.deepcopy(t))
                                            yield t
                                        elif enclitic == 'st':
                                            if token.endswith('ust'):
                                                t.text = (token[:-len(enclitic)])
                                                t.startchar = start_char
                                                t.endchar = start_char + len(token[:-len(enclitic)]) - len(enclitic)
                                                if mode == 'index':
                                                    self._cache.append(copy.deepcopy(t))
                                                yield t
                                                t.text = 'est'
                                                t.startchar = start_char + len(token[:-len(enclitic)])
                                                t.endchar = start_char + len(token[:-len(enclitic)]) + len(enclitic)
                                                if mode == 'index':
                                                    self._cache.append(copy.deepcopy(t))
                                                yield t
                                            else:
                                                t.text = (token[:-len(enclitic)])
                                                t.startchar = start_char
                                                t.endchar = start_char + len(token[:-len(enclitic)]) - len(enclitic)
                                                if mode == 'index':
                                                    self._cache.append(copy.deepcopy(t))
                                                yield t
                                                t.text = 'est'
                                                t.startchar = start_char + len(token[:-len(enclitic)])
                                                t.endchar = start_char + len(token[:-len(enclitic)]) + len(enclitic)
                                                if mode == 'index':
                                                    self._cache.append(copy.deepcopy(t))
                                                yield t
                                        elif enclitic == "'s":
                                            t.text = token + 's'
                                            t.startchar = start_char
                                            t.endchar = start_char + len(token)
                                            if mode == 'index':
                                                self._cache.append(copy.deepcopy(t))
                                            yield t
                                            t.text = 'es'
                                            t.startchar = start_char + len(token) + 1
                                            t.endchar = start_char + len(token) + len(enclitic)
                                            if mode == 'index':
                                                self._cache.append(copy.deepcopy(t))
                                            yield t
                                        else:
                                            t.text = (token[:-len(enclitic)])
                                            t.startchar = start_char
                                            t.endchar = start_char + len(token[:-len(enclitic)])
                                            if mode == 'index':
                                                self._cache.append(copy.deepcopy(t))
                                            yield t
                                            t.text = enclitic
                                            t.startchar = start_char + len(token[:-len(enclitic)])
                                            t.endchar = start_char + len(token[:-len(enclitic)]) + len(enclitic)
                                            if mode == 'index':
                                                self._cache.append(copy.deepcopy(t))
                                            yield t
                                        is_enclitic = True
                                        break
                            if not is_enclitic:
                                t.text = token
                                if chars:
                                    t.startchar = start_char + ldiff
                                    t.endchar = start_char + original_length - rdiff  # - ndiff - rdiff
                                if mode == 'index':
                                    self._cache.append(copy.deepcopy(t))
                                yield t
                            start_char += original_length
                        start_char += 1


class CachedLASLATokenizer(Tokenizer):
    def __init__(self, **kwargs):
        super(CachedLASLATokenizer, self).__init__()
        self.__dict__.update(**kwargs)
        self._cache = None
        self._docix = None

    @property
    def cache(self):
        return copy.deepcopy(self._cache)

    def __call__(self, value: dict, positions=False, chars=False,
                 keeporiginal=True, removestops=True, tokenize=True,
                 start_pos=0, start_char=0, mode='', **kwargs):
        if kwargs.get('docix', None) == self._docix and self._cache:
            yield from self.cache
        else:
            t = engine.analysis.acore.CylleneusToken(positions, chars, removestops=removestops, mode=mode, **kwargs)

            if t.mode == 'query':
                t.original = t.text = value.translate(jvmap)
                yield t
            else:
                if not tokenize:
                    t.original = t.text = '\n'.join([el for el in value['text']])
                    t.boost = 1.0
                    if positions:
                        t.pos = start_pos
                    if chars:
                        t.startchar = start_char
                        t.endchar = start_char + len(value['text'])
                    yield t
                else:
                    from corpus.lasla import parse_bpn

                    self._cache = []
                    self._docix = kwargs.get('docix', None)

                    punctmap = str.maketrans('', '', '[{(<>)}]')
                    added = re.compile(r"(\s?[<(][\w .]+[>)]\s?)")

                    t.boost = 1.0
                    t.pos = t.startchar = t.endchar = 0

                    sect_sent = 0  # sentence count within passage
                    sent_id = '0001'
                    sect_pos = 0   # word pos within passage
                    sent_pos = 0    # word pos within sentence
                    current_refs = tuple(['0'] * len(value['meta']))
                    nflag = None
                    morpho_buffer = None
                    for pos, line in enumerate(value['text']):
                        t.pos = pos

                        parsed = parse_bpn(line)

                        if not parsed:
                            continue

                        if int(parsed['sent_id']) > int(sent_id):
                            sent_pos = 1
                            sent_id = parsed['sent_id']
                            if tuple([int(i) for i in parsed['refs'].split(',')]) > current_refs:
                                sect_sent = 1
                                sect_pos = 1
                            else:
                                sect_sent += 1

                        if keeporiginal:
                            if added.search(parsed['form']):
                                t.original = added.sub('', parsed['form'])
                            else:
                                t.original = parsed['form']
                        t.stopped = False

                        if parsed['form_code'] in '&+':
                            if parsed['lemma'] != '#':
                                if parsed['lemma'] == '_SVM':
                                    t.morpho = None
                                    t.lemma = parsed['lemma']
                                    t.lemma_n = parsed['lemma_n']
                                    t.original = added.sub('', parsed['form'])
                                    t.text = parsed['form'].translate(punctmap)
                                else:
                                    form = parsed['form']
                                    t.morpho = parsed['morpho']

                                    if ' ' in form:
                                        t.original = added.sub('', form)
                                        text = form.translate(punctmap)
                                    else:
                                        t.original = form
                                        text = form
                                    t.lemma = parsed['lemma']
                                    t.lemma_n = parsed['lemma_n']
                                    if added.search(parsed['form']):
                                        t.original = added.sub('', parsed['form'])
                                    t.text = text.translate(punctmap)
                                    nflag = False
                            else:
                                # could be a Greek form, do we index it?
                                t.morpho = ''
                                t.lemma = ''
                                t.lemma_n = ''
                                t.original = added.sub('', parsed['form'])
                                t.text = parsed['form'].translate(punctmap)
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
                            'meta': value['meta'].lower()
                        }
                        tags = value['meta'].split('-')
                        if len(tags) > 2 and 'line' in tags:
                            tags.pop(tags.index('line'))
                        divs = {i: div.lower() for i, div in enumerate(tags)}
                        refs = tuple(parsed['refs'].strip().split(','))
                        for i in range(len(divs)):
                            meta[divs[i]] = refs[i]

                        current_refs = tuple([int(ref) for ref in refs]) # int(ref)?

                        t.morphosyntax = parsed['subord']

                        meta['sect_sent'] = str(sect_sent)
                        meta['sect_pos'] = str(sect_pos)
                        meta['sent_id'] = parsed['sent_id']
                        meta['sent_pos'] = str(sent_pos)
                        t.meta = meta
                        t.startchar = start_char
                        t.endchar = start_char + len(t.original)

                        if t.text != t.original:
                            tc = copy.deepcopy(t)
                            tc.text = t.original
                            yield tc

                        yield t
                        sent_pos += 1
                        sect_pos += 1
                        start_char += len(t.original) + 1


class CachedPROIELTokenizer(Tokenizer):
    def __init__(self, **kwargs):
        super(CachedPROIELTokenizer, self).__init__()
        self.__dict__.update(**kwargs)
        self._cache = None
        self._docix = None

    @property
    def cache(self):
        return copy.deepcopy(self._cache)

    def __call__(self, data: ElementTree, positions=True, chars=True,
                 keeporiginal=True, removestops=True, tokenize=True,
                 start_pos=0, start_char=0, mode='', **kwargs):
        if kwargs.get('docix', None) == self._docix and self._cache:
            yield from self.cache
        else:
            self._cache = []
            self._docix = kwargs.get('docix', None)

            t = CylleneusToken(positions, chars, removestops=removestops, mode=mode, **kwargs)
            if t.mode == 'query':
                t.original = t.text = data.translate(jvmap)
                yield t
            else:
                if not tokenize:
                    t.original = ''
                    for token in data.findall('.//token'):
                        form = token.get('form')
                        if not form:
                            continue
                        after = token.get('presentation-after', '')
                        before = token.get('presentation-before', '')
                        t.original += f"{before}{form}{after}"
                    t.text = t.original
                    t.boost = 1.0
                    if positions:
                        t.pos = start_pos
                    if chars:
                        t.startchar = start_char
                        t.endchar = start_char + len(t.original)
                    yield t
                else:
                    from corpus.proiel import parse_proiel

                    for sentence in data['text'].findall('.//sentence'):
                        for pos, token in enumerate(sentence.findall('.//token')):
                            form = token.get('form')
                            if not form:
                                continue
                            else:
                                form = form.replace(' ', ' ').replace(' ', ' ')
                                form = re.sub(r"\.([^ ]|^$)", r'. \1', form)
                            t.lemma = token.get('lemma')
                            t.morpho = parse_proiel(token.get('part-of-speech'), token.get('morphology'))
                            t.morphosyntax = token.get('relation', None)
                            t.boost = 1.0

                            meta = {
                                'meta': data['meta'].lower()
                            }
                            for i, div in enumerate(data['meta'].split('-')):
                                meta[div] = token.get('citation-part').split('.')[i]
                            meta['sent_id'] = sentence.get('id')
                            meta['sent_pos'] = token.get('id')
                            t.meta = meta

                            before = token.get('presentation-before', '')
                            after = token.get('presentation-after', '')

                            if keeporiginal:
                                t.original = f"{before}{form}{after}"
                            t.stopped = False
                            if positions:
                                t.pos = start_pos + pos
                            original_len = len(form)

                            if form.istitle() and pos == 0 and not t.lemma.istitle():
                                form = form.lower()
                            t.text = form
                            if chars:
                                t.startchar = start_char + len(before)
                                t.endchar = start_char + len(before) + original_len
                            self._cache.append(copy.deepcopy(t))
                            yield t

                            if form in editorial:
                                t.text = editorial[form]
                                self._cache.append(copy.deepcopy(t))
                                yield t
                            start_char += len(before) + len(form) + len(after)

class CachedAGLDTTokenizer(Tokenizer):
    def __init__(self, **kwargs):
        super(CachedAGLDTTokenizer, self).__init__()
        self.__dict__.update(**kwargs)
        self._cache = None
        self._docix = None

    @property
    def cache(self):
        return copy.deepcopy(self._cache)

    def __call__(self, data: ElementTree, positions=True, chars=True,
                 keeporiginal=True, removestops=True, tokenize=True,
                 start_pos=0, start_char=0, mode='', **kwargs):
        if kwargs.get('docix', None) == self._docix and self._cache:
            yield from self.cache
        else:
            self._cache = []
            self._docix = kwargs.get('docix', None)

            t = CylleneusToken(positions, chars, removestops=removestops, mode=mode, **kwargs)
            if t.mode == 'query':
                t.original = t.text = data.translate(jvmap)
                yield t
            else:
                if not tokenize:
                    t.original = ''
                    for token in data.findall('.//token'):
                        form = token.get('form')
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
                    from corpus.agldt import agldt2wn

                    for sentence in data['text'].findall('.//sentence'):
                        for pos, token in enumerate(sentence.findall('.//word')):
                            form = token.get('form')
                            if not form:
                                continue
                            else:
                                form = form.replace(' ', ' ').replace(' ', ' ')
                                form = re.sub(r"\.([^ ]|^$)", r'. \1', form)
                            lemma = token.get('lemma')
                            if lemma in ('.', ',', 'punc1', 'comma1', 'PERIOD1'):
                                continue
                            t.lemma = token.get('lemma', None)
                            t.morpho = agldt2wn(token.get('postag'))
                            t.morphosyntax = token.get('relation', None)
                            t.boost = 1.0

                            meta = {
                                'meta': data['meta'].lower()
                            }
                            divs = data['meta'].split('-')
                            for i, div in enumerate(divs):
                                if not (len(divs) > 2 and div == 'line'):
                                    meta[div] = sentence.get('subdoc').split('.')[i]
                            meta['sent_id'] = sentence.get('id')
                            meta['sent_pos'] = token.get('id')
                            t.meta = meta

                            if keeporiginal:
                                t.original = f"{form}"
                            t.stopped = False
                            if positions:
                                t.pos = start_pos + pos
                            original_len = len(form)

                            if form.istitle() and pos == 0 and not t.lemma.istitle():
                                form = form.lower()
                            t.text = form
                            if chars:
                                t.startchar = start_char
                                t.endchar = start_char + original_len
                            self._cache.append(copy.deepcopy(t))
                            yield t

                            if form in editorial:
                                t.text = editorial[form]
                                self._cache.append(copy.deepcopy(t))
                                yield t
                            start_char += len(form)
