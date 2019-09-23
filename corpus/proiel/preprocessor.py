import codecs
from datetime import datetime
from pathlib import Path

import lxml.etree as et
from corpus.preprocessing import BasePreprocessor

from .core import AUTHOR_TAB


class Preprocessor(BasePreprocessor):
    def parse(self, file: Path):
        with codecs.open(file, 'rb') as f:
            value = f.read()
        parser = et.XMLParser(encoding='utf-8')
        doc = et.XML(value, parser=parser)

        _author = doc.find('source').find('author').text
        _title = doc.find('source').find('title').text

        author = AUTHOR_TAB[_author]['author']
        title = AUTHOR_TAB[_author]['works'][_title]['title']
        meta = AUTHOR_TAB[_author]['works'][_title]['meta']
        urn = AUTHOR_TAB[_author]['works'][_title]['urn']
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
