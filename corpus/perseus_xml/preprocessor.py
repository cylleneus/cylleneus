import codecs
from datetime import datetime
from pathlib import Path

import lxml.etree as et
from corpus.phi5 import AUTHOR_TAB
from corpus.preprocessing import BasePreprocessor


class Preprocessor(BasePreprocessor):
    def parse(self, file: Path):
        auth_code, work_code, _, _ = file.name.split('.')
        urn = 'urn:cts:latinLit:' + f"{auth_code}.{work_code}"
        author = AUTHOR_TAB[auth_code]['author']
        title = AUTHOR_TAB[auth_code]['works'][work_code]['title']

        with codecs.open(file, 'rb') as f:
            value = f.read()
        parser = et.XMLParser(encoding='utf-8')

        doc = et.XML(value, parser=parser)

        divs = [
            cref.get('unit')
            for cref in doc.findall(".//{http://www.tei-c.org/ns/1.0}refState")
        ]
        meta = '-'.join(divs)

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
            'filename': file.name,
            'datetime': datetime.now()
        }
