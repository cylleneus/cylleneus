from collections import namedtuple
from pathlib import Path

import settings
from engine.fields import Schema
from engine.schemas import schemas
from engine.searching import CylleneusHit, CylleneusSearcher

from . import agldt, default, indexer, lasla, latin_library, perseus, perseus_xml, proiel


CorpusMeta = namedtuple('CorpusMeta', [
    'schema',
    'tokenizer',
    'glob',
    'fetch'
])

# meta = {
#     'agldt': CorpusMeta(
#         agldt.schema.DocumentSchema,
#         agldt.tokenizer.Tokenizer,
#         agldt.core.glob,
#         agldt.core.get
#     ),
#     'default': CorpusMeta(
#         default.DocumentSchema,
#         default.Tokenizer,
#         default.glob,
#         default.fetch
#     ),
# }


class Corpus:
    def __init__(self, name: str, schema: Schema=None):
        self._name = name
        self._schema = schema if schema else schemas.get(self.name)()

        # self._schema = meta.get(name, meta['default']).schema()
        # self._tokenizer = meta.get(name, meta['default']).tokenizer()
        # self._glob = meta.get(name, meta['default']).glob

    # @property
    # def glob(self):
    #     return self._glob
    #
    # @property
    # def tokenizer(self):
    #     return self._tokenizer

    @property
    def name(self):
        return self._name

    @property
    def schema(self):
        return self._schema

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
                return Work(doc=doc).indexer

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
        work = Work(self, doc=hit)
        urn, reference, text = work.get(meta, fragment)
        return self.name, work.author, work.title, urn, reference, text

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name and \
            self.schema == other.schema and \
            self.path == other.path


# Get function for generic 'imported' corpus
def plaintext_get(hit, meta, fragment):
    content = hit['content']
    offset = content.find(fragment)

    # Reference and hlite values
    start = ', '.join(
        [f"{k}: {v}" for k, v in meta['start'].items() if v]
    )
    end = ', '.join(
        [f"{k}: {v}" for k, v in meta['end'].items() if v]
    )
    reference = '-'.join([start, end]) if end != start else start
    hlite_start = [
        v - offset
        if k != 'pos' and v is not None else v
        for k, v in meta['start'].items()
    ]
    hlite_end = [
        v - offset
        if k != 'pos' and v is not None else v
        for k, v in meta['end'].items()
    ]

    # Collect text and context
    lbound = fragment.rfind(' ', 0, settings.CHARS_OF_CONTEXT)
    rbound = fragment.find(' ', -(settings.CHARS_OF_CONTEXT - (meta['start']['endchar'] - meta['start']['startchar'])))

    pre = f"<pre>{fragment[:lbound]}</pre>"
    post = f"<post>{fragment[rbound + 1:]}</post>"

    endchar = lbound + 1 + (hlite_start[-2] - hlite_start[-3])
    hlite = f"<em>{fragment[lbound + 1:endchar]}</em>" + fragment[endchar:rbound]
    match = f"<match>{hlite}</match>"

    text = f' '.join([pre, match, post])
    return None, reference, text


get_router = {
    'plaintext': plaintext_get,
    'agldt': agldt.get,
    'perseus': perseus.get,
    'perseus_xml': perseus_xml.get,
    'lasla': lasla.get,
    'latin_library': latin_library.get,
    'proiel': proiel.get,
}


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
        else:
            if author and title:
                docs = list(indexer.Indexer.docs_for(corpus, author, title))
                if docs:
                    doc = list(indexer.Indexer.docs_for(corpus, author, title))[0][1]
                    self._doc = doc
                    self._docix = doc['docix']
                    self._author = doc['author']
                    self._title = doc['title']
                else:
                    self._doc = self._author = self._title = None
            else:
                self._doc = self._author = self._title = None
        self._indexer = indexer.Indexer(corpus, self)

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

    def get(self, meta, fragment):
        return get_router[self.corpus.name](self.doc, meta, fragment)

    def __str__(self):
        return f"{self.author}, {self.title} [{self.corpus.name}]"

    def __repr__(self):
        return f"Work(corpus={self.corpus}, docix={self.docix})"

    def __eq__(self, other):
        return self.docix == other.docix and self.corpus == other.corpus
