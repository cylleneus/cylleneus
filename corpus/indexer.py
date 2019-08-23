import shutil
from pathlib import Path

import engine.index
from engine.fields import Schema
from engine.schemas import schemas
from engine.writing import CLEAR
from utils import slugify
from .preprocessing import *


class IndexingError(Exception):
    pass


class Indexer:
    @classmethod
    def docs_for(cls, corpus, author: str='*', title: str='*'):
        paths = corpus.index_dir.glob(f"{slugify(author)}/{slugify(title)}")
        for path in paths:
            if engine.index.exists_in(path):
                ix = engine.index.open_dir(path, schema=corpus.schema)
                yield from ix.reader().iter_docs()

    def __init__(self, corpus, work):
        self._corpus = corpus
        self._work = work
        if work.author and work.title:
            self._path = Path(self.corpus.index_dir / slugify(work.author) / slugify(work.title))
        else:
            self._path = None
        self._schema = schemas.get(self.corpus.name)()
        self._preprocessor = preprocessors.get(corpus.name, DefaultPreprocessor)()

        if self.path and engine.index.exists_in(self.path):
            self._index = engine.index.open_dir(self.path, schema=self.schema)
        else:
            self._index = None

    @property
    def work(self):
        return self._work

    @property
    def corpus(self):
        return self._corpus

    @corpus.setter
    def corpus(self, cp):
        self._corpus = cp

    @property
    def preprocessor(self):
        return self._preprocessor

    def iter_docs(self):
        yield from self.index.reader().iter_docs()

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
    def index(self):
        if self._index:
            return self._index

    @index.setter
    def index(self, ix):
        self._index = ix

    @property
    def path(self):
        if self._path:
            return Path(self._path)

    @path.setter
    def path(self, p: Path):
        self._path = p

    def clear(self):
        with self.index.writer() as writer:
            writer.commit(mergetype=CLEAR)

    def destroy(self):
        if self.path.exists():
            shutil.rmtree(self.path)
            self._index = None

    def optimize(self):
        self.index.optimize()

    def create(self):
        if not self.index:
            if not self.path.exists():
                self.path.mkdir(parents=True)
            engine.index.create_in(self.path, schema=self.schema)

    def open(self):
        if not engine.index.exists_in(self.path):
            self.create()
        self.index = engine.index.open_dir(self.path, schema=self.schema)

    def update(self, path: Path):
        if self.path and self.path.exists():
            self.destroy()
        self.from_file(path)

    def from_file(self, path: Path):
        if self.path and self.path.exists():
            self.destroy()

        if path.exists():
            docix = self.corpus.doc_count_all

            kwargs = self.preprocessor.parse(path)
            if 'author' not in kwargs and self.work.author:
                kwargs['author'] = self.work.author
            if 'title' not in kwargs and self.work.title:
                kwargs['title'] = self.work.title

            self.path = Path(self.corpus.index_dir / slugify(kwargs['author']) / slugify(kwargs['title']))
            self.open()

            writer = self.index.writer(limitmb=1024)
            writer.add_document(corpus=self.corpus.name, docix=docix, **kwargs)
            writer.commit()

    def from_string(self, content: str, **kwargs):
        if content:
            docix = self.corpus.doc_count_all

            parsed = self.preprocessor.parse(content)
            kwargs.update(parsed)

            ix = self.open()

            writer = ix.writer(limitmb=1024)
            writer.add_document(corpus=self.corpus.name, docix=docix, **kwargs)
            writer.commit()
