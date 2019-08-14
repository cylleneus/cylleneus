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


def imported_get(hit, meta, fragment):
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
    'imported': imported_get,
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
