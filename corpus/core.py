from collections import namedtuple
from pathlib import Path

import settings
from engine.fields import Schema
from engine.searching import CylleneusHit, CylleneusSearcher

from . import agldt, default, lasla, latin_library, perseus, perseus_xml, proiel
from . import indexer


CorpusMeta = namedtuple('CorpusMeta', [
    'schema',
    'tokenizer',
    'preprocessor',
    'glob',
    'fetch'
])

meta = {
    'agldt': CorpusMeta(
        agldt.DocumentSchema,
        agldt.Tokenizer,
        agldt.Preprocessor,
        agldt.core.glob,
        agldt.core.fetch
    ),
    'lasla': CorpusMeta(
        lasla.DocumentSchema,
        lasla.Tokenizer,
        lasla.Preprocessor,
        lasla.core.glob,
        lasla.core.fetch
    ),
    'latin_library': CorpusMeta(
        default.DocumentSchema,
        default.Tokenizer,
        latin_library.Preprocessor,
        latin_library.core.glob,
        latin_library.core.fetch
    ),
    'perseus': CorpusMeta(
        perseus.DocumentSchema,
        perseus.Tokenizer,
        perseus.Preprocessor,
        perseus.core.glob,
        perseus.core.fetch
    ),
    'perseus_xml': CorpusMeta(
        perseus_xml.DocumentSchema,
        perseus_xml.Tokenizer,
        perseus_xml.Preprocessor,
        perseus_xml.core.glob,
        perseus_xml.core.fetch
    ),
    'proiel': CorpusMeta(
        proiel.DocumentSchema,
        proiel.Tokenizer,
        proiel.Preprocessor,
        proiel.core.glob,
        proiel.core.fetch
    ),
    'default': CorpusMeta(
        default.DocumentSchema,
        default.Tokenizer,
        default.Preprocessor,
        default.glob,
        default.fetch
    ),
}


class Corpus:
    def __init__(self, name: str, schema: Schema=None):
        self._name = name

        _meta = meta.get(name, meta['default'])
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
        for path in self.index_dir.glob('*/*'):
            yield Work(self, author=path.parts[-2], title=path.name)

    def works_for(self, author: str='*', title: str ='*'):
        for path in self.index_dir.glob(f'{author}/{title}'):
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
            if docix in ixr.index.reader().all_doc_ixs():
                ixr.destroy()

    @property
    def doc_count_all(self):
        return sum([reader.doc_count_all() for reader in self.readers])

    def all_doc_ixs(self):
        docixs = []
        for ixr in self.indexers:
            docixs.extend(ixr.index.reader().all_doc_ixs())
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
        return Path(self.path / 'index')

    @property
    def text_dir(self):
        return Path(self.path / 'text')

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
            if doc['docix'] == int(docix):
                return Work(corpus=self, doc=doc).indexer

    @property
    def readers(self):
        for ixr in self.indexers:
            if ixr.index:
                yield ixr.index.reader()

    def readers_for(self, author: str='*', title: str='*'):
        for ixr in self.indexers_for(author, title):
            yield ixr.index.reader()

    def reader_for_docix(self, docix: int):
        for reader in self.readers:
            ids = list(reader.all_doc_ixs())
            if docix in ids:
                return reader

    @property
    def path(self):
        return Path(f"{settings.ROOT_DIR}/corpus/{self.name}")

    def fetch(self, hit, meta, fragment):
        work = Work(corpus=self, doc=hit)
        urn, reference, text = work.fetch(work, meta, fragment)
        return self.name, work.author, work.title, urn, reference, text

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name and \
            self.schema == other.schema and \
            self.path == other.path


class Work:
    def __init__(self, corpus: Corpus, author: str=None, title: str=None, doc: CylleneusHit=None):
        self._corpus = corpus
        if doc:
            self._doc = doc
            if 'author' in self.doc:
                self._author = self.doc['author']
            if 'title' in self.doc:
                self._title = self.doc['title']
            if 'docix' in self.doc:
                self._docix = self.doc['docix']
            if 'urn' in self.doc:
                self._urn = self.doc['urn']
            else:
                self._urn = None
            if 'filename' in self.doc:
                self._filename = self.doc['filename']
            else:
                self._filename = None
            if 'datetime' in self.doc:
                self._timestamp = self.doc['datetime']
            else:
                self._timestamp = None
        else:
            if author and title:
                docs = list(indexer.Indexer.docs_for(corpus, author, title))
                if docs:
                    doc = list(indexer.Indexer.docs_for(corpus, author, title))[0][1]
                    self._doc = doc
                    self._docix = doc['docix']
                    self._author = doc['author']
                    self._title = doc['title']
                    self._urn = doc.get('urn', None)
                    self._filename = doc.get('filename', None)
                    self._timestamp = doc.get('datetime', None)
                else:
                    self._doc = self._author = self._title = self._urn = \
                        self._filename = self._timestamp = None
            else:
                self._doc = self._author = self._title = self._urn = \
                    self._filename = self._timestamp = None
        self._indexer = indexer.Indexer(corpus, self)
        self.fetch = self.corpus._fetch

    @property
    def is_searchable(self):
        return self.corpus.schema and self.index

    @property
    def indexer(self):
        return self._indexer

    @property
    def index(self):
        return self.indexer.index

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
            self._docix = list(self.indexer.iter_docs())[0][0]
        return self._docix

    @property
    def doc(self):
        return self._doc

    @property
    def meta(self):
        if self.doc and 'meta' in self.doc:
            return self.doc['meta']

    @property
    def divs(self):
        return [d.lower() for d in self.meta.split('-')]

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def urn(self):
        return self._urn

    @property
    def filename(self):
        return Path(self._filename)

    def __str__(self):
        return f"{self.author}, {self.title} [{self.corpus.name}]"

    def __repr__(self):
        return f"Work(corpus={self.corpus}, docix={self.docix})"

    def __eq__(self, other):
        return self.docix == other.docix and self.corpus == other.corpus
