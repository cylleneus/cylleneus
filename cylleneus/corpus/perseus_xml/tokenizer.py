import copy
import re
import string

from cylleneus.engine.analysis.acore import CylleneusToken
from cylleneus.engine.analysis.tokenizers import Tokenizer
from cylleneus.lang.latin import PunktLatinCharsVars, compound, enclitics, exceptions, jvmap, proper_names, \
    punctuation, \
    replacements, convert_diphthongs, strip_diacritics
from cylleneus.utils import flatten, stringify


class CachedTokenizer(Tokenizer):
    def __init__(self, **kwargs):
        super(CachedTokenizer, self).__init__()
        self._cache = None
        self._docix = None
        self.cached = True
        self.__dict__.update(**kwargs)

    @property
    def cache(self):
        return copy.deepcopy(self._cache)

    def __call__(self, value, positions=True, chars=True,
                 keeporiginal=True, removestops=True, tokenize=True,
                 start_pos=0, start_char=0, mode='', **kwargs):
        if kwargs.get('docix', None) == self._docix and self._cache is not None:
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
                    divs = [
                        cref.get('n')
                        for cref in doc.findall(".//{http://www.tei-c.org/ns/1.0}cRefPattern")
                    ]
                    tei_base = "/tei:TEI/tei:text/tei:body/tei:div"
                    # Prose divisions
                    sentences = doc.xpath(
                        tei_base + ("/tei:div" * len(divs)),
                        namespaces={
                            'tei': 'http://www.tei-c.org/ns/1.0'
                        }
                    )
                    # Fall back to poetry divisions
                    if len(sentences) == 0:
                        sentences = doc.xpath(
                            tei_base +
                            ("/tei:div" * (len(divs)-1)) + "/tei:l",
                            namespaces={
                                'tei': 'http://www.tei-c.org/ns/1.0'
                            }
                        )
                    # Fall back to speaker divisions (plays)
                    if len(sentences) == 0:
                        sentences = doc.xpath(
                            tei_base +
                            ("/tei:div" * (len(divs)-1)) + "/tei:sp/tei:l",
                            namespaces= {
                                'tei': 'http://www.tei-c.org/ns/1.0'
                            }
                        )
                    for i, sentence in enumerate(sentences):
                        meta = {
                            'meta': '-'.join(divs),
                            divs[-1]: sentence.get('n'),
                            'sent_id': i
                        }

                        el = sentence
                        j = -1
                        while el is not None:
                            if el.getparent() is not None:
                                if el.getparent().get('type', None) == 'textpart' \
                                    or el.getparent().tag == '{http://www.tei-c.org/ns/1.0}sp':
                                    if el.getparent().tag == '{http://www.tei-c.org/ns/1.0}sp':
                                        meta['speaker'] = el.getparent().find(
                                            './/{http://www.tei-c.org/ns/1.0}speaker').text
                                    elif el.getparent().get('type', None) == 'textpart':
                                        j -= 1
                                        meta[divs[j]] = el.getparent().get('n')
                            el = el.getparent()

                        text = sentence.text
                        # If the text is not embedded in an XML node, use the 'text' attribute

                        if not text:
                            text = stringify(sentence)

                        if not text:
                            continue

                        tokens = []
                        temp_tokens = tokenizer.word_tokenize(text.strip())

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
                            token = convert_diphthongs(strip_diacritics(token)).translate(jvmap)

                            if positions:
                                t.pos = start_pos + pos
                            if token == ' ' or token in punctuation or token in stopchars:
                                pos += 1
                                continue
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
                                    t.endchar = start_char + original_length - rdiff
                                if mode == 'index':
                                    self._cache.append(copy.deepcopy(t))
                                yield t
                            start_char += original_length
                        start_char += 1
