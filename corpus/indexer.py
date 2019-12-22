import queue
import shutil
from pathlib import Path

import engine.index
from engine.writing import CLEAR
from utils import DEBUG_HIGH, DEBUG_MEDIUM, print_debug, slugify


class IndexingError(Exception):
    pass


class Indexer:
    @classmethod
    def docs_for(cls, corpus, author: str = "*", title: str = "*"):
        paths = corpus.index_dir.glob(f"{slugify(author)}/{slugify(title)}")
        for path in paths:
            indexes = Path(path).glob('*.toc')
            for index in indexes:
                indexname = '_'.join(index.name.replace('.toc', '').split('_')[1:5])
                if engine.index.exists_in(path, indexname=indexname):
                    ix = engine.index.open_dir(path, schema=corpus.schema, indexname=indexname)
                    yield from ix.reader().iter_docs()

    def __init__(self, corpus, work, language='lat'):
        self._corpus = corpus
        self._work = work
        self._language = language
        self._indexes = []

        if work.author and work.title:
            self._path = Path(
                self.corpus.index_dir / slugify(work.author) / slugify(work.title)
            )
        else:
            self._path = None

        if self.path:
            indexes = Path(self.path).glob('*.toc')

            for index in indexes:
                indexname = ('_'.join(index.name.replace('.toc', '').rsplit('_', maxsplit=4)[:4])).strip('_')

                if engine.index.exists_in(self.path, indexname=indexname):
                    ix = engine.index.open_dir(self.path, schema=corpus.schema, indexname=indexname)
                    self._indexes.append(ix)

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
    def indexes(self):
        if self._indexes:
            return self._indexes

    @indexes.setter
    def indexes(self, ixs):
        self._indexes = ixs

    @property
    def path(self):
        if self._path:
            return Path(self._path)

    @path.setter
    def path(self, p: Path):
        self._path = p

    def iter_docs(self):
        for ix in self.indexes:
            yield from ix.reader().iter_docs()

    def clear(self):
        for ix in self.indexes:
            with ix.writer() as writer:
                writer.commit(mergetype=CLEAR)

    def destroy(self):
        if self.path and self.path.exists():
            shutil.rmtree(self.path)
            self._indexes = []

    def optimize(self):
        for ix in self.indexes:
            ix.optimize()

    def create(self, indexname: str = None):
        if not self.path.exists():
            self.path.mkdir(parents=True)
        engine.index.create_in(self.path, schema=self.corpus.schema, indexname=indexname)

    def open(self, indexname: str):
        if not engine.index.exists_in(self.path, indexname=indexname):
            self.create(indexname=indexname)
        ix = engine.index.open_dir(self.path, schema=self.corpus.schema, indexname=indexname)
        return ix

    def update(self, path: Path):
        if self.path and self.path.exists():
            self.destroy()
        docix = self.from_file(path)
        return docix

    def from_file(self, path: Path):
        if self.path and self.path.exists():
            self.destroy()

        if path.exists():
            docix = self.corpus.doc_count_all

            kwargs = self.corpus.preprocessor.parse(path)
            if "author" not in kwargs and self.work.author:
                kwargs["author"] = self.work.author
            if "title" not in kwargs and self.work.title:
                kwargs["title"] = self.work.title
            kwargs["corpus"] = self.corpus.name
            kwargs["docix"] = docix

            self.path = Path(
                self.corpus.index_dir
                / slugify(kwargs["author"])
                / slugify(kwargs["title"])
            )
            ix = self.open(indexname=f"{self.corpus.name}_{slugify(kwargs['author'])}_{slugify(kwargs['title'])}"
                                     f"_{docix}")

            writer = ix.writer(limitmb=4096, procs=1, multisegment=True)
            try:
                print_debug(
                    DEBUG_MEDIUM,
                    "Add document: {}, {} [{}] to '{}' [{}]".format(
                        kwargs["author"], kwargs["title"], path, self.corpus.name, docix
                    ),
                )
                writer.add_document(**kwargs)
                writer.commit()
            except queue.Empty as e:
                pass

            return docix

    def from_string(self, content: str, **kwargs):
        if self.path and self.path.exists():
            self.destroy()

        if content:
            docix = self.corpus.doc_count_all

            parsed = self.corpus.preprocessor.parse(content)
            kwargs.update(parsed)

            self.path = Path(
                self.corpus.index_dir
                / slugify(kwargs["author"])
                / slugify(kwargs["title"])
            )
            ix = self.open(indexname=f"{self.corpus.name}_{slugify(kwargs['author'])}_{slugify(kwargs['title'])}"
                                     f"_{docix}")

            writer = ix.writer(limitmb=4096, procs=1, multisegment=True)
            try:
                print_debug(
                    DEBUG_MEDIUM,
                    "Add document: '{}', {}, {}, {} [...]".format(
                        self.corpus.name,
                        docix,
                        kwargs["author"],
                        kwargs["title"],
                    ),
                )
                writer.add_document(corpus=self.corpus.name, docix=docix, **kwargs)
                writer.commit()
            except queue.Empty as e:
                pass

            return docix
