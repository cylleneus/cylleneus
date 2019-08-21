import shutil
from pathlib import Path

from engine import index
from engine.fields import Schema
from engine.schemas import schemas
from engine.writing import CLEAR
from utils import slugify
from .preprocessing import *


class IndexingError(Exception):
    pass


class Indexer:
    def __init__(self, corpus):
        self._corpus = corpus
        self._schema = schemas.get(self.corpus.name)()
        self._preprocessor = preprocessors.get(corpus.name, DefaultPreprocessor)()

    @property
    def corpus(self):
        return self._corpus

    @corpus.setter
    def corpus(self, cp):
        self._corpus = cp

    @property
    def preprocessor(self):
        return self._preprocessor

    @property
    def doc_count_all(self):
        return sum([ix.reader().doc_count_all() for ix in self.indices])

    def iter_docs(self):
        for ix in self.indices:
            yield from ix.reader().iter_docs()

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
        ixs = []
        for author in self.path.glob('*'):
            for title in author.glob('*'):
                if index.exists_in(title):
                    ix = index.open_dir(title, schema=self.schema)
                    ixs.append(ix)
        return ixs

    def all_doc_nums(self):
        docnums = []
        for ix in self.indices:
            docnums.extend(ix.reader().all_doc_nums())
        return docnums

    def indices_for(self, author: str=None, title: str=None):
        ixs = []

        if author and title:
            try:
                ix = index.open_dir(str(self.path / author / title))
            except index.EmptyIndexError:
                pass
            else:
                ixs.append(ix)
        elif author:
            for d in self.path.glob(f"{slugify(author)}/*"):
                if index.exists_in(d):
                    try:
                        ix = index.open_dir(d, schema=self.schema)
                    except index.EmptyIndexError:
                        continue
                    else:
                        ixs.append(ix)
        else:
            for d in self.path.glob(f'*/{slugify(title)}'):
                if index.exists_in(d):
                    try:
                        ix = index.open_dir(d, schema=self.schema)
                    except index.EmptyIndexError:
                        continue
                    else:
                        ixs.append(ix)
        return ixs

    @property
    def path(self):
        return Path(self.corpus.path / 'index')

    def clear(self):
        for ix in self.indices:
            with ix.writer() as writer:
                writer.commit(mergetype=CLEAR)

    def destroy(self):
        if self.path.exists():
            shutil.rmtree(self.path)
            self._indices = []

    def optimize(self):
        for ix in self.indices:
            ix.optimize()

    def create_in(self, path: Path):
        d = Path(self.path / path)
        if not d.exists():
            d.mkdir(parents=True)
        index.create_in(str(d), schema=self.schema)

    def open(self, path: Path):
        d = Path(self.path / path)
        if not index.exists_in(str(path)):
            self.create_in(d)
        ix = index.open_dir(str(d), schema=self.schema)
        return ix

    def delete(self, path: Path):
        d = Path(self.path / path)
        shutil.rmtree(str(d))

    def delete_by(self, author: str = '*', title: str = '*'):
        paths = self.path.glob(f"{slugify(author)}/{slugify(title)}")
        for path in paths:
            self.delete(path)

    def delete_by_num(self, docnum: int):
        for ix in self.indices:
            if docnum in ix.reader().all_doc_nums():
                ix.storage.destroy()

    def update(self, author: str, title: str, path: Path):
        a_slug = slugify(author)
        t_slug = slugify(title)
        d = Path(self.path / a_slug / t_slug)
        self.delete(d)
        self.add(path, author, title)

    def add(self, path: Path, author: str = None, title: str = None):
        if path.exists():
            docix = self.doc_count_all

            kwargs = self.preprocessor.parse(path)
            if 'author' not in kwargs and author:
                kwargs['author'] = author
            if 'title' not in kwargs and title:
                kwargs['title'] = title
            kwargs['docnum'] = docix

            a_slug = slugify(kwargs['author'])
            t_slug = slugify(kwargs['title'])

            d = Path(self.path / a_slug / t_slug)
            ix = self.open(d)

            writer = ix.writer(docbase=docix,
                limitmb=1024,
            )
            writer.add_document(docix=docix, **kwargs)
            writer.commit()
        self.optimize()

    def adds(self, content: str, **kwargs):
        if content:
            ndocs = self.doc_count_all

            docix = ndocs
            parsed = self.preprocessor.parse(content)
            kwargs.update(parsed)

            a_slug = slugify(kwargs['author'])
            t_slug = slugify(kwargs['title'])

            d = Path(self.path / a_slug / t_slug)
            ix = self.open(d)

            writer = ix.writer(docbase=docix, limitmb=1024)
            writer.add_document(docix=docix, **kwargs)
            writer.commit()
        self.optimize()
