import codecs
from datetime import datetime
from pathlib import Path

import lxml.etree as et
from cylleneus.corpus.preprocessing import BasePreprocessor


class Preprocessor(BasePreprocessor):
    def parse(self, file: Path):
        with codecs.open(file, 'rb') as f:
            value = f.read()
        parser = et.XMLParser(encoding='utf-8')
        doc = et.XML(value, parser=parser)

        urn = doc.find('head').findall('referenceSystem')[0].get("sourceName")
        author = "Amenemope"
        title = "Instructions"
        meta = "page-line"

        data = {'text': doc, 'meta': meta}

        return {
            'urn':      urn,
            'author':   author,
            'title':    title,
            'language': 'egy',
            'meta':     meta,
            'form':     data,
            'lemma':    data,
            # 'synset':       data,
            # 'annotation':   data,
            # 'semfield':     data,
            # 'morphosyntax': data,
            'mapping':  data,
            'filename': file.name,
            'datetime': datetime.now()
        }
