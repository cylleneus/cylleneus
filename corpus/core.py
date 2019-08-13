import settings
from engine import fields, index

from . import lasla, latin_library, perseus


class Corpus:
    def __init__(self, name: str, ix: index.FileIndex = None,
                 schema: fields.Schema = None):
        self._name = name

        if ix and isinstance(ix, index.FileIndex):
            self._index = ix
        else:
            if index.exists_in(settings.ROOT_DIR + f"/index/{name}"):
                self._index = index.open_dir(settings.ROOT_DIR + f"/index/{name}")
            else:
                self._index = None

        if schema and isinstance(schema, fields.Schema):
            self._schema = schema
        else:
            if self._index:
                self._schema = self._index.schema
            else:
                self._schema = None

    @property
    def name(self):
        return self._name

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, i):
        self._index = i

    @property
    def schema(self):
        return self._schema

    @schema.setter
    def schema(self, s):
        self._schema = s

    @property
    def reader(self):
        return self.index.reader()

    def __str__(self):
        return self.name

    def fetch(self, hit, meta, fragment):
        work = Work(self, hit)
        urn, reference, text = work.get(meta, fragment)

        return work.author, work.title, urn, reference, text


get_router = {
    'perseus': perseus.get,
    'lasla': lasla.get,
    'latin_library': latin_library.get,
}


class Work:
    def __init__(self, corpus, hit):
        self._corpus = corpus
        self._hit = hit

        if hit.get('author', False):
            self._author = hit['author']
        else:
            self._author = None

        if hit.get('title', False):
            self._title = hit['title']
        else:
            self._title = None

        if hit.get('meta', False):
            self._meta = hit['meta']
        else:
            self._meta = None

    @property
    def author(self):
        return self._author

    @property
    def title(self):
        return self._title

    @property
    def corpus(self):
        return self._corpus

    @property
    def hit(self):
        return self._hit

    @property
    def meta(self):
        return self._meta

    @property
    def divs(self):
        return [d.lower() for d in self.meta.split('-')]

    def get(self, meta, fragment):
        return get_router[self.corpus.name](self.hit, meta, fragment)
