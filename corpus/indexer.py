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
            if engine.index.exists_in(path):
                ix = engine.index.open_dir(path, schema=corpus.schema)
                yield from ix.reader().iter_docs()

    def __init__(self, corpus, work, language='lat'):
        self._corpus = corpus
        self._work = work
        self._language = language
        if work.author and work.title:
            self._path = Path(
                self.corpus.index_dir / slugify(work.author) / slugify(work.title)
            )
        else:
            self._path = None

        if self.path and engine.index.exists_in(self.path):
            self._index = engine.index.open_dir(self.path, schema=self.corpus.schema)
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

    def iter_docs(self):
        yield from self.index.reader().iter_docs()

    def clear(self):
        with self.index.writer() as writer:
            writer.commit(mergetype=CLEAR)

    def destroy(self):
        if self.path and self.path.exists():
            shutil.rmtree(self.path)
            self._index = None

    def optimize(self):
        self.index.optimize()

    def create(self, indexname: str = None):
        if not self.index:
            if not self.path.exists():
                self.path.mkdir(parents=True)
            engine.index.create_in(self.path, schema=self.corpus.schema, indexname=indexname)

    def open(self, indexname: str = None):
        if not engine.index.exists_in(self.path):
            self.create(indexname=indexname)
        self.index = engine.index.open_dir(self.path, schema=self.corpus.schema, indexname=indexname)

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
            self.open(indexname=f"{self.corpus.name}_{kwargs['author']}_{kwargs['title']}_{docix}")

            writer = self.index.writer(limitmb=4096, procs=1, multisegment=True)
            try:
                print_debug(
                    DEBUG_MEDIUM,
                    "Add document: '{}', {}, {}, {} [{}]".format(
                        self.corpus.name, docix, kwargs["author"], kwargs["title"], path
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
            self.open()

            writer = self.index.writer(limitmb=4096, procs=1, multisegment=True)
            try:
                print_debug(
                    DEBUG_HIGH,
                    "Add document: '{}', {}, {}, {} [...]".format(
                        self.corpus.name,
                        docix,
                        kwargs["author"],
                        kwargs["title"],
                        end="...",
                    ),
                )
                writer.add_document(corpus=self.corpus.name, docix=docix, **kwargs)
                writer.commit()
                print_debug(DEBUG_HIGH, "ok")
            except queue.Empty as e:
                pass
            return docix
