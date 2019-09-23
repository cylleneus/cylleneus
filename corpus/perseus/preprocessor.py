import codecs
import json
from datetime import datetime
from pathlib import Path

from corpus.preprocessing import BasePreprocessor


class Preprocessor(BasePreprocessor):
    def parse(self, file: Path):
        with codecs.open(file, 'r', 'utf8') as f:
            data = json.load(f)

        return {
            'author': data['author'].title(),
            'title': data['originalTitle'].title(),
            'meta': data['meta'].lower(),
            'urn': data['original-urn'].rsplit('.', maxsplit=1)[0] if 'original-urn' in data else "",
            'form': data,
            'lemma': data,
            'synset': data,
            'annotation': data,
            'semfield': data,
            'filename': file.name,
            'datetime': datetime.now()
        }
