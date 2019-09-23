import codecs
from datetime import datetime
from pathlib import Path

import lxml.etree as et
from corpus.phi5 import AUTHOR_TAB
from corpus.preprocessing import BasePreprocessor


class Preprocessor(BasePreprocessor):
    def parse(self, file: Path):
        with codecs.open(file, 'rb') as f:
            value = f.read()
        parser = et.XMLParser(encoding='utf-8')
        doc = et.XML(value, parser=parser)

        urn = doc.get('cts')

        auth_code, work_code = urn.rsplit(':', maxsplit=1)[1].split('.')[:2]

        author = AUTHOR_TAB[auth_code]['author']
        title = AUTHOR_TAB[auth_code]['works'][work_code]['title']
        meta = AUTHOR_TAB[auth_code]['works'][work_code]['meta']

        data = {'text': doc, 'meta': meta}

        return {
            'urn': urn,
            'author': author,
            'title': title,
            'meta': meta,
            'form': data,
            'lemma': data,
            'synset': data,
            'annotation': data,
            'semfield': data,
            'morphosyntax': data,
            'filename': file.name,
            'datetime': datetime.now()
        }
