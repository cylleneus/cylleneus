from pathlib import Path

from cylleneus import settings
from cylleneus.engine.fields import Schema
from cylleneus.engine.searching import CylleneusHit, CylleneusSearcher
from cylleneus.utils import slugify

from .manifest import meta
from . import indexer


class Corpus:
    def __init__(self, name: str):
        self._name = name

        _meta = meta.get(name, meta["default"])
        self._schema = _meta.schema()
        self._tokenizer = _meta.tokenizer()
        self._preprocessor = _meta.preprocessor(self)
        self._glob = _meta.glob
        self._fetch = _meta.fetch

    @property
    def name(self):
        return self._name

    @property
    def preprocessor(self):
        return self._preprocessor

    @preprocessor.setter
    def preprocessor(self, p):
        self._preprocessor = p

    @property
    def schema(self):
        return self._schema

    @schema.setter
    def schema(self, s: Schema):
        self._schema = s

    @property
    def glob(self):
        return self._glob

    @glob.setter
    def glob(self, g):
        self._glob = g

    def optimize(self):
        for ixr in self.indexers:
            ixr.optimize()

    @property
    def is_searchable(self):
        return self.schema and any([work.is_searchable for work in self.works])

    @property
    def works(self):
        for path in self.index_dir.glob("*/*"):
            yield Work(self, author=path.parts[-2], title=path.name)

    def works_for(self, author: str = None, title: str = None):
        for path in self.index_dir.glob(
            f'{slugify(author) if author else "*"}/{slugify(title) if title else "*"}'
        ):
            yield Work(self, author=path.parts[-2], title=path.name)

    def work_by_docix(self, docix: int):
        for _docix, doc in self.iter_docs():
            if _docix == docix:
                return Work(self, doc=doc)

    def destroy(self):
        for ixr in self.indexers:
            ixr.destroy()

    def delete_by(self, **kwargs):
        for reader in self.readers:
            with CylleneusSearcher(reader) as searcher:
                results = searcher.document_numbers(**kwargs)
                if results:
                    for docix in results:
                        self.delete_by_ix(docix)

    def delete_by_ix(self, docix: int):
        for ixr in self.indexers:
            for ix in ixr.indexes:
                if docix in ix.reader().all_doc_ixs():
                    ixr.destroy()

    @property
    def doc_count_all(self):
        return sum([reader.doc_count_all() for reader in self.readers])

    def all_doc_ixs(self):
        docixs = []
        for ixr in self.indexers:
            for ix in ixr.indexes:
                docixs.extend(ix.reader().all_doc_ixs())
        return docixs

    def clear(self):
        for ixr in self.indexers:
            ixr.clear()

    def update(self, docix: int, path: Path):
        ixr = self.indexer_for_docix(docix)
        ixr.update(path)

    def update_by(self, author: str, title: str, path: Path):
        ixr = list(self.indexers_for(author, title))[0]
        docix = ixr.update(path)
        return docix

    @property
    def index_dir(self):
        return Path(self.path / "index")

    @property
    def text_dir(self):
        return Path(self.path / "text")

    def iter_docs(self):
        for reader in self.readers:
            yield from reader.iter_docs()

    @property
    def indexers(self):
        for work in self.works:
            yield work.indexer

    def indexers_for(self, author: str = None, title: str = None):
        ixrs = (work.indexer for work in self.works_for(author, title))
        yield from ixrs

    def indexer_for_docix(self, docix: int):
        for doc in self.iter_docs():
            if doc["docix"] == int(docix):
                return Work(corpus=self, doc=doc).indexer

    @property
    def readers(self):
        for ixr in self.indexers:
            if ixr.indexes:
                for ix in ixr.indexes:
                    yield ix.reader()

    def readers_for(self, author: str = "*", title: str = "*"):
        for ixr in self.indexers_for(author, title):
            for ix in ixr.indexes:
                yield ix.reader()

    def reader_for_docix(self, docix: int):
        for reader in self.readers:
            ids = list(reader.all_doc_ixs())
            if docix in ids:
                return reader

    @property
    def path(self):
        return Path(f"{settings.CORPUS_DIR}/{self.name}")

    def fetch(self, hit, meta, fragment):
        work = Work(corpus=self, doc=hit)
        urn, reference, text = work.fetch(work, meta, fragment)
        return self.name, work.author, work.title, urn, reference, text

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return (
            self.name == other.name
            and self.schema == other.schema
            and self.path == other.path
        )


class Work:
    def __init__(
        self,
        corpus: Corpus,
        author: str = None,
        title: str = None,
        doc: CylleneusHit = None,
        language="lat",
    ):
        self._corpus = corpus
        if doc:
            self._doc = [
                doc,
            ]
            if "author" in doc:
                self._author = doc["author"]
            if "title" in doc:
                self._title = doc["title"]
            if "docix" in doc:
                self._docix = [doc["docix"], ]
            if "urn" in doc:
                self._urn = doc["urn"]
            else:
                self._urn = None
            if "filename" in doc:
                self._filename = [doc["filename"],]
            else:
                self._filename = None
            if "datetime" in doc:
                self._timestamp = doc["datetime"]
            else:
                self._timestamp = None
            if "language" in doc:
                self._language = doc["language"]
        else:
            if author and title:
                docs = [
                    doc[1] for doc in indexer.Indexer.docs_for(corpus, author, title)
                ]
                if docs:
                    self._doc = docs
                    self._docix = [doc["docix"] for doc in docs]
                    self._author = self.doc[0]["author"]
                    self._title = self.doc[0]["title"]
                    self._urn = self.doc[0].get("urn", None)
                    self._filename = [doc.get("filename", None) for doc in self.doc]
                    self._timestamp = self.doc[0].get("datetime", None)
                else:
                    self._doc = self._urn = self._filename = self._timestamp = None
                    self._author = author
                    self._title = title
            else:
                self._doc = self._author = self._title = self._urn = self._filename = self._timestamp = None
        self._indexer = indexer.Indexer(corpus, self)
        self.fetch = self.corpus._fetch
        self._language = language

    @property
    def is_searchable(self):
        return self.corpus.schema and self.indexes

    @property
    def language(self):
        return self._language

    @property
    def indexer(self):
        return self._indexer

    @property
    def indexes(self):
        return self.indexer.indexes

    @property
    def author(self):
        return self._author

    @property
    def title(self):
        return self._title

    def delete(self):
        self.indexer.destroy()

    @property
    def corpus(self):
        return self._corpus

    @property
    def docix(self):
        if not self.doc:
            self._docix = [doc[1]["docix"] for doc in self.indexer.iter_docs()]
        return self._docix

    @property
    def doc(self):
        return self._doc

    @property
    def meta(self):
        if self.doc and "meta" in self.doc[0]:
            return self.doc[0]["meta"]

    @property
    def divs(self):
        return [d.lower() for d in self.meta.split("-")]

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def urn(self):
        return self._urn

    @property
    def filename(self):
        return self._filename[0]

    def __str__(self):
        return f"{self.author}, {self.title} [{self.corpus.name}]"

    def __repr__(self):
        return f"Work(corpus={self.corpus}, docix={self.docix})"

    def __eq__(self, other):
        return self.docix == other.docix and self.corpus == other.corpus
