import config
from engine import fields, index

from . import lasla, latin_library, perseus


class Corpus:
    def __init__(self, name: str, ix: index.FileIndex = None,
                 schema: fields.Schema = None):
        self._name = name

        if ix and isinstance(ix, index.FileIndex):
            self._index = ix
        else:
            if index.exists_in(config.ROOT_DIR + f"/index/{name}"):
                self._index = index.open_dir(config.ROOT_DIR + f"/index/{name}")
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
        (reference, hlite), text = work.get(meta, fragment)

        return work.author, work.title, (reference, hlite), text


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
        text = get_router[self.corpus.name](self.hit, meta, fragment)

        if self.meta and meta:
            divs = self.divs

            start = ', '.join(
                [f"{item}: {meta['start'][item]}" for item in meta['start'] if item in divs]
            )
            end = ', '.join(
                [f"{item}: {meta['end'][item]}" for item in meta['end'] if item in divs]
            )
            reference = '-'.join([start, end]) if end != start else start
            hlite = [meta['start'][item] for item in meta['start'] if item not in divs], \
                    [meta['end'][item] for item in meta['end'] if item not in divs]
        elif meta:
            start = ', '.join(
                [f"{k}: {v}" for k, v in meta['start'].items() if v]
            )
            end = ', '.join(
                [f"{k}: {v}" for k, v in meta['end'].items() if v]
            )
            reference = '-'.join([start, end]) if end != start else start
            hlite = meta['start'].values(), meta['end'].values()
        else:
            reference = None
            hlite = None
        return (reference, hlite), text


# class Author:
#     def __init__(self, name, reader):
#         self._name = name
#         self._works = {doc['originalTitle']: Work(doc) for doc in reader.docs() if doc['author'] == self.name}
#
#     @property
#     def name(self):
#         return self._name
#
#     @property
#     def works(self):
#         return self._works
#
#
# class Reference:
#     def __init__(self):
#         self._work_id: int = 0
#         self._chapter: int = 0
#         self._paragraph: int = 0 # verse for poetry
#         self._line_in_paragraph: int = 0
#         self._word_in_line: int = 0
#         self._book: int = 0
#         self._order_in_work: int = 0
#
#     def __str__(self):
#         return f"{self.work_id} {self.chapter:3} {self.paragraph:4} {self.line_in_paragraph:3} {self.word_in_line:3}"
#         # does it include book refs too? order_in_work?
#
#     def __gt__(self, other):
#         if self.chapter < other.chapter:
#             return False
#         elif self.chapter == other.chapter:
#             if self.paragraph < other.paragraph:
#                 return False
#             elif self.paragraph == other.paragraph:
#                 if self.line_in_paragraph < other.line_in_graph:
#                     return False
#                 elif self.line_in_paragraph == other.line_in_paragraph:
#                     if self.word_in_line < other.word_in_line:
#                         return False
#         return True
#
#     def __lt__(self, other):
#         if self.chapter > other.chapter:
#             return False
#         elif self.chapter == other.chapter:
#             if self.paragraph > other.paragraph:
#                 return False
#             elif self.paragraph == other.paragraph:
#                 if self.line_in_paragraph > other.line_in_graph:
#                     return False
#                 elif self.line_in_paragraph == other.line_in_paragraph:
#                     if self.word_in_line > other.word_in_line:
#                         return False
#         return True
#
#     def __eq__(self, other):
#         if self.chapter == other.chapter and self.paragraph == other.paragraph and \
#                 self.line_in_paragraph == other.line_in_paragraph and self.word_in_line == other.word_in_line:
#             return True
#         else:
#             return False
#
#
# class Token:
#     def __init__(self, form, lemma=None, index=None, reference=None, morphology=None, syntax=None, raw_index=None):
#         self._lemma = lemma
#         self._index = index
#         self._form = form
#         self._morphology = morphology
#         self._reference = reference
#         self._syntax = syntax
#         self._raw_index = raw_index
#
#     @property
#     def raw_index(self):
#         return self._raw_index
#
#     @property
#     def form(self):
#         return self._form
#
#     @property
#     def morphology(self):
#         return self._morphology
#
#     @property
#     def lemma(self):
#         return self._lemma
#
#     @property
#     def index(self):
#         return self._index
#
#     @property
#     def reference(self):
#         return self._reference
#
#     @property
#     def refs(self):
#         return Reference(*self.reference.split(' ')) if self.reference else None
