import codecs
import re
from datetime import datetime
from pathlib import Path

from corpus.preprocessing import BasePreprocessor

from .core import AUTHOR_TAB


class Preprocessor(BasePreprocessor):
    def parse(self, file: Path):
        code = file.name.lstrip('LAT').rstrip('.txt')
        auth_code, work_code = code.split('-')
        auth_code = 'phi' + auth_code
        work_code = 'phi' + work_code

        with codecs.open(file, 'r', 'utf8') as f:
            doc = f.read()
            content = re.sub(r".*?\t", "", doc)
            data = {'text': doc, 'meta': AUTHOR_TAB[auth_code]['works'][work_code]['meta']}
        return {
            'code':       code,
            'author':     AUTHOR_TAB[auth_code]['author'],
            'title':      AUTHOR_TAB[auth_code]['works'][work_code]['title'],
            'language':   'lat',
            'source':     AUTHOR_TAB[auth_code]['works'][work_code]['source'],
            'meta':       AUTHOR_TAB[auth_code]['works'][work_code]['meta'],
            'content':    content,
            'form':       data,
            'lemma':      data,
            'synset':     data,
            'annotation': data,
            'semfield':   data,
            'filename':   file.name,
            'datetime':   datetime.now()
        }
