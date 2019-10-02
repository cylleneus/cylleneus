import copy
import re
import string

from engine.analysis.acore import CylleneusToken
from engine.analysis.tokenizers import Tokenizer
from lang.latin import jvmap
from utils import alnum

from .core import parse_bpn


class CachedTokenizer(Tokenizer):
    def __init__(self, **kwargs):
        super(CachedTokenizer, self).__init__()
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
            t = CylleneusToken(positions, chars, removestops=removestops, mode=mode, **kwargs)

            if t.mode == 'query':
                t.original = value
                t.text = value.translate(jvmap)
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
                    self._cache = []
                    self._docix = kwargs.get('docix', None)

                    punctuation = str.maketrans('', '', string.punctuation)
                    editorial = str.maketrans('', '', '[{(<>)}]')
                    added = re.compile(r"(\s?[<(][\w .]+[>)]\s?)")

                    t.boost = 1.0
                    t.pos = t.startchar = t.endchar = 0

                    sect_sent = 0  # sentence count within passage
                    sent_id = '0001'
                    sect_pos = 0   # word pos within passage
                    sent_pos = 0    # word pos within sentence
                    current_refs = tuple(['0'] * len(value['meta']))
                    nflag = None
                    for pos, line in enumerate(value['text']):
                        t.pos = pos

                        parsed = parse_bpn(line)

                        if not parsed:
                            continue

                        if int(parsed['sent_id']) > int(sent_id):
                            sent_pos = 0
                            sent_id = parsed['sent_id']
                            if tuple([alnum(i) for i in parsed['refs'].split(',')]) > current_refs:
                                sect_sent = 1
                                sect_pos = 0
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
                                    t.text = parsed['form'].translate(editorial)
                                else:
                                    form = parsed['form']
                                    t.morpho = parsed['morpho']

                                    if ' ' in form:
                                        t.original = added.sub('', form)
                                        text = form.translate(editorial)
                                    else:
                                        t.original = form
                                        text = form
                                    t.lemma = parsed['lemma']
                                    t.lemma_n = parsed['lemma_n']
                                    if added.search(parsed['form']):
                                        t.original = added.sub('', parsed['form'])
                                    t.text = text.translate(editorial)
                                    nflag = False
                            else:
                                # could be a Greek form, do we index it?
                                t.morpho = ''
                                t.lemma = ''
                                t.lemma_n = ''
                                t.original = added.sub('', parsed['form'])
                                t.text = parsed['form'].translate(editorial)
                        elif parsed['form_code'] == '@':  # combined forms
                            if parsed['lemma'] != '#':
                                t.lemma = parsed['lemma']
                                t.lemma_n = parsed['lemma_n']
                                t.text = parsed['form'].translate(editorial)
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
                            t.text = parsed['form'].translate(editorial)
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
                        divs = {i: div.lower() for i, div in enumerate(tags)}
                        refs = tuple([ref.translate(punctuation) for ref in parsed['refs'].strip().split(',')])
                        for i in range(len(divs)):
                            meta[divs[i]] = refs[i]

                        current_refs = refs

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
