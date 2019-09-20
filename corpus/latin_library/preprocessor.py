import codecs
import re
from datetime import datetime
from pathlib import Path

from corpus.preprocessing import BasePreprocessor

from .core import FILE_TAB


class Preprocessor(BasePreprocessor):
    def parse(self, file: Path):
        path = str(file.relative_to(self.corpus.text_dir)).replace('\\', '/')

        author = FILE_TAB[path]['author']
        title = FILE_TAB[path]['title']

        with codecs.open(file, 'r', 'utf8') as fp:
            doc = fp.read()

        # Do some tidying up
        subs = [
            (r"\.,", "."),
            (r"([\w])\.([\w])", r"\1. \2"),
            (r",([\w])", r", \1"),
            (r"(?<=\w)\.\.", r" . ."),
            (r"([.,;:])([.,;:])", r"\1 \2"),
            (r"[\t\r\n ]+", " "),
            (r'\.\"', r'\"\.'),
            (r' ,', ','),
            (r'\[ \d+ \] ', ''),
            (r' \[,', '[,'),
            (r'\]\.', '.]')
        ]
        for pattern, repl in subs:
            doc = re.sub(pattern, repl, doc)
        return {
            'author': author,
            'title': title,
            'content': doc,
            'form': doc,
            'lemma': doc,
            'synset': doc,
            'annotation': doc,
            'semfield': doc,
            'filename': str(file.relative_to(self.corpus.text_dir)),
            'datetime': datetime.now()
        }
