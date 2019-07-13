from corpus import Corpus
import engine.index
from engine import fields
from engine import writing
from pathlib import Path
from engine.qparser.default import QueryParser
from . import preprocessing
from engine import schemas


class IndexingError(Exception):
    pass

class Indexer:
    def __init__(self, corpus: Corpus):
        self._corpus = corpus
        self._index = corpus.index
        self._schema = corpus.index.schema if corpus.index else None
        self._preprocessor = preprocessing.preprocessors.get(corpus.name,
                                                             preprocessing.DefaultPreprocessor)()

    @property
    def corpus(self):
        return self._corpus

    @corpus.setter
    def corpus(self, cp: Corpus):
        self._corpus = cp

    @property
    def preprocessor(self):
        return self._preprocessor

    @corpus.setter
    def corpus(self, p: preprocessing.Preprocessor):
        self._preprocessor = p

    @property
    def schema(self):
        if not self._schema:
            self._schema = schemas.schemas.get(self.corpus.name)()
        return self._schema

    @schema.setter
    def schema(self, s: fields.Schema):
        self._schema = s

    @property
    def docs(self):
        if self.index:
            return self.index.reader().iter_docs()

    @property
    def index(self):
        if not self._index:
            self.open()
        return self._index

    @index.setter
    def index(self, ix: engine.index.Index):
        self._index = ix

    def clear(self):
        with self.index.writer() as writer:
            writer.commit(mergetype=writing.CLEAR)

    def optimize(self):
        if self.index:
            self.index.optimize()

    def create(self):
        self.index = engine.index.create_in(f'index/{self.corpus.name}',
                                            schema=self.schema,
                                            indexname=self.corpus.name)

    def open(self):
        if not engine.index.exists_in(f'index/{self.corpus.name}',
                                      indexname=self.corpus.name):
            self.create()
        self.index = engine.index.open_dir(f'index/{self.corpus.name}',
                                     schema=self.schema,
                                     indexname=self.corpus.name)

    def delete(self, docnum: int=None):
        if docnum:
            writer = self.index.writer()
            writer.delete_document(docnum)
            writer.commit()
        else:
            self.clear()

    def delete_by(self, author: str = None, title: str = None):
        if not self.index:
            self.open()
        if author and title:
            if 'author' in self.schema and 'title' in self.schema:
                parser = QueryParser("form", self.schema)
                # TODO: possibly add '' around {author} and {title}?
                query = parser.parse(f"(author:{author} AND title:{title})")
                self.index.writer().delete_by_query(query)
        elif author:
            if 'author' in self.schema:
                writer = self.index.writer()
                writer.delete_by_term("author", author)
                writer.commit()
        elif title:
            if 'title' in self.schema:
                writer = self.index.writer()
                writer.delete_by_term("title", title)
                writer.commit()

    def update(self, docnum: int, path: Path):
        if not self.index:
            self.open()
        else:
            self.delete(docnum)
        self.add(path)

    def update_by(self, author: str, title: str, path: Path):
        if not self.index:
            self.open()
        if author and title:
            if 'author' in self.schema and 'title' in self.schema:
                parser = QueryParser("form", self.schema)
                # TODO: possibly add '' around {author} and {title}?
                query = parser.parse(f"(author:{author} AND title:{title})")
                writer = self.index.writer()
                writer.delete_by_query(query)
                writer.commit()
        elif author:
            if 'author' in self.schema:
                writer = self.index.writer()
                writer.delete_by_term("author", author)
                writer.commit()
        elif title:
            if 'title' in self.schema:
                writer = self.index.writer()
                writer.delete_by_term("title", title)
                writer.commit()
        self.add(path)

    def add(self, path: Path, author=None, title=None):
        if path.exists():
            if not self.index:
                self.open()
            ndocs = self.index.doc_count_all()

            if path.is_dir():
                files = path.glob('*.*')
            elif path.is_file():
                files = [path,]
            else:
                files = []

            writer = self.index.writer(
                limitmb=512,
                procs=4 if len(files) > 1 else 1,
                multisegment=True if len(files) > 1 else False
            )
            for i, file in enumerate(files):
                docix = i + ndocs
                kwargs = self.preprocessor.parse(file)
                if author:
                    kwargs['author'] = author
                if title:
                    kwargs['title'] = title
                writer.add_document(docix=docix, **kwargs)
            writer.commit()

    def adds(self, s: str, author=None, title=None):
        if s:
            ndocs = self.index.doc_count_all()

            writer = self.index.writer(
                limitmb=512,
                procs=1,
                multisegment=False,
            )

            docix = ndocs
            kwargs = preprocessing.preprocessors['default']().parse(s)
            if author:
                kwargs['author'] = author
            if title:
                kwargs['title'] = title
            writer.add_document(docix=docix, **kwargs)
        writer.commit()
