import codecs
from datetime import datetime
from pathlib import Path

from cylleneus.corpus.preprocessing import BasePreprocessor


class Preprocessor(BasePreprocessor):
    def parse(self, file: Path):
        filename = file.name
        author = "-"
        title = filename.rstrip('.conllu').split('-')[0]

        urn = filename.rstrip('.conllu')
        meta = "chapter-line"

        with codecs.open(file, 'r', 'utf8') as fp:
            doc = fp.readlines()
        data = {
            'text': doc,
            'meta': meta
        }
        return {
            'author':       author,
            'title':        title,
            'language':     'skt',
            'urn':          urn,
            'meta':         meta,
            'form':         data,
            'lemma':        data,
            'synset':       data,
            'annotation':   data,
            'semfield':     data,
            'morphosyntax': data,
            'filename':     file.name,
            'datetime':     datetime.now()
        }
