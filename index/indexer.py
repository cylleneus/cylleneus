import shutil
from pathlib import Path

from engine import index
from corpus import Corpus
from engine.fields import Schema
from engine.schemas import schemas
from engine.writing import CLEAR
from utils import slugify
from .preprocessing import *


class IndexingError(Exception):
    pass


class Indexer:
    def __init__(self, corpus: Corpus):
        self._corpus = corpus
        self._schema = schemas.get(self.corpus.name)()
        self._preprocessor = preprocessors.get(corpus.name, DefaultPreprocessor)()

        self._indices = []
        for author in self.corpus.path.glob('*'):
            for title in author.glob('*'):
                if index.exists_in(title):
                    ix = index.open_dir(title, schema=self.schema)
                    self._indices.append(ix)

    @property
    def corpus(self):
        return self._corpus

    @corpus.setter
    def corpus(self, cp: Corpus):
        self._corpus = cp

    @property
    def preprocessor(self):
        return self._preprocessor

    @property
    def doc_count_all(self):
        return len(self.indices)

    @corpus.setter
    def corpus(self, p: Preprocessor):
        self._preprocessor = p

    @property
    def schema(self):
        return self._schema

    @schema.setter
    def schema(self, s: Schema):
        self._schema = s

    @property
    def docs(self):
        for ix in self.indices:
            yield from ix.reader().iter_docs()

    @property
    def indices(self):
        return self._indices

    def clear(self):
        for ix in self.indices:
            with ix.writer() as writer:
                writer.commit(mergetype=CLEAR)

    def destroy(self):
        for path in self.corpus.path.glob('*'):
            if index.exists_in(path):
                shutil.rmtree(path)
                self._indices = []

    def optimize(self):
        for ix in self.indices:
            ix.optimize()

    def create_in(self, path: Path):
        d = Path(self.corpus.path + path)
        if not d.exists():
            d.mkdir(parents=True)
        index.create_in(str(d), schema=self.schema)

    # e.g. /lasla/caesar/bg
    def open(self, path: Path):
        d = Path(self.corpus.path + path)
        if not index.exists_in(str(path)):
            self.create_in(d)
        ix = index.open_dir(str(d), schema=self.schema)
        return ix

    def delete(self, path: Path):
        d = Path(self.corpus.path + path)
        if index.exists_in(str(d)):
            shutil.rmtree(str(d))

    def delete_by(self, author: str = '*', title: str = '*'):
        paths = Path.glob(f"{str(self.corpus.path)}/{slugify(author)}/{slugify(title)}")
        for path in paths:
            self.delete(path)

    def update(self, author: str, title: str, path: Path):
        a_slug = slugify(author)
        t_slug = slugify(title)
        d = Path(f"{str(self.corpus.path)}/{a_slug}/{t_slug}")
        self.delete(d)
        self.add(path, author, title)

    def add(self, path: Path, author: str = None, title: str = None):
        if path.exists():
            a_slug = slugify(author)
            t_slug = slugify(title)

            d = Path(f"{str(self.corpus.path)}/{a_slug}/{t_slug}")
            ix = self.open(d)

            writer = ix.writer(
                limitmb=1024,
            )
            docix = self.doc_count_all + 1
            kwargs = self.preprocessor.parse(path)
            if 'author' not in kwargs and author:
                kwargs['author'] = author
            if 'title' not in kwargs and title:
                kwargs['title'] = title
            writer.add_document(docix=docix, **kwargs)
            writer.commit()

    def adds(self, content: str, **kwargs):
        if content:
            ndocs = self.index.doc_count_all()

            writer = self.index.writer(limitmb=512)

            docix = ndocs
            parsed = self.preprocessor.parse(content)
            kwargs.update(parsed)

            writer.add_document(docix=docix, **kwargs)
            writer.commit()
