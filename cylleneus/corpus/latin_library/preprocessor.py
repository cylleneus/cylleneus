import codecs
from datetime import datetime
from pathlib import Path
import re

from cylleneus.corpus.preprocessing import BasePreprocessor

from .core import FILE_TAB


class Preprocessor(BasePreprocessor):
    def parse(self, file: Path):
        path = str(file.relative_to(self.corpus.text_dir)).replace('\\', '/')

        author = FILE_TAB[path]['author']
        title = FILE_TAB[path]['title']

        with codecs.open(file, 'r', 'utf8') as fp:
            doc = fp.read()

        doc = re.sub(r'(\s)+', r'\1', doc)

        return {
            'author':     author,
            'title':      title,
            'language':   'lat',
            'form':       doc,
            'lemma':      doc,
            'synset':     doc,
            'annotation': doc,
            'semfield':   doc,
            'filename':   str(file.relative_to(self.corpus.text_dir)),
            'datetime':   datetime.now()
        }
