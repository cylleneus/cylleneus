from engine import index
from engine import fields
from pathlib import Path
import codecs
import json


class Corpus:
    def __init__(self, name: str, ix: index.FileIndex = None,
                 schema: fields.Schema = None):
        # self._authors = {doc['author']: Author(doc['author'], self.reader) for doc in reader.docs()}
        self._name = name

        if ix and isinstance(ix, index.FileIndex):
            self._index = ix
        else:
            if index.exists_in(f"index/{name}"):
                self._index = index.open_dir(f"index/{name}")
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

    # @property
    # def authors(self):
    #     return self._authors

    # def remove(self, s: str) # remove an author or work from the corpus (move to unused)
    # def add(self, s: str) # move an unused author or work back into the corpus
    # def reset(self) # reset the corpus to its original state
    # def list(self) # list all authors or works in corpus currently

    def load(self, filename):
        if self.name == 'perseus':
            # TODO: remove
            filename = Path(filename).name
            with codecs.open(f'corpus/text/perseus/{filename}', 'r', 'utf8') as fp:
                doc = json.load(fp)
            return Work(self.name, filename, doc)

class Author:
    def __init__(self, name, reader):
        self._name = name
        self._works = {doc['originalTitle']: Work(doc) for doc in reader.docs() if doc['author'] == self.name}

    @property
    def name(self):
        return self._name

    @property
    def works(self):
        return self._works

class Work:
    def __init__(self, corpus, filename, doc):
        if corpus == 'perseus':
            self._corpus = corpus
            self._filename = filename
            self._author = doc['author']
            self._text = doc['text']
            self._edition = doc['edition']
            self._english_title = doc['englishTitle']
            self._source = doc['source']
            self._original_title = doc['originalTitle']
            self._original_urn = doc['original-urn']
            self._language = doc['language']
            self._source_link = doc['sourceLink']
            self._urn = doc['urn']
            self._meta = doc['meta']

    @property
    def meta(self):
        return self._meta

    @property
    def divs(self):
        return [d.lower() for d in self.meta.split('-')]

    @property
    def text(self):
        return self._text

    def get(self, start, end):
        # TODO: collect all text from start to end
        item = self.text
        for div in self.meta.split('-'):
            item = item[start[div.lower()]]
        return item

class Reference:
    def __init__(self):
        self._work_id: int = 0
        self._chapter: int = 0
        self._paragraph: int = 0 # verse for poetry
        self._line_in_paragraph: int = 0
        self._word_in_line: int = 0
        self._book: int = 0
        self._order_in_work: int = 0

    def __str__(self):
        return f"{self.work_id} {self.chapter:3} {self.paragraph:4} {self.line_in_paragraph:3} {self.word_in_line:3}"
        # does it include book refs too? order_in_work?

    def __gt__(self, other):
        if self.chapter < other.chapter:
            return False
        elif self.chapter == other.chapter:
            if self.paragraph < other.paragraph:
                return False
            elif self.paragraph == other.paragraph:
                if self.line_in_paragraph < other.line_in_graph:
                    return False
                elif self.line_in_paragraph == other.line_in_paragraph:
                    if self.word_in_line < other.word_in_line:
                        return False
        return True

    def __lt__(self, other):
        if self.chapter > other.chapter:
            return False
        elif self.chapter == other.chapter:
            if self.paragraph > other.paragraph:
                return False
            elif self.paragraph == other.paragraph:
                if self.line_in_paragraph > other.line_in_graph:
                    return False
                elif self.line_in_paragraph == other.line_in_paragraph:
                    if self.word_in_line > other.word_in_line:
                        return False
        return True

    def __eq__(self, other):
        if self.chapter == other.chapter and self.paragraph == other.paragraph and \
                self.line_in_paragraph == other.line_in_paragraph and self.word_in_line == other.word_in_line:
            return True
        else:
            return False


class Token:
    def __init__(self, form, lemma=None, index=None, reference=None, morphology=None, syntax=None, raw_index=None):
        self._lemma = lemma
        self._index = index
        self._form = form
        self._morphology = morphology
        self._reference = reference
        self._syntax = syntax
        self._raw_index = raw_index

    @property
    def raw_index(self):
        return self._raw_index

    @property
    def form(self):
        return self._form

    @property
    def morphology(self):
        return self._morphology

    @property
    def lemma(self):
        return self._lemma

    @property
    def index(self):
        return self._index

    @property
    def reference(self):
        return self._reference

    @property
    def refs(self):
        return Reference(*self.reference.split(' ')) if self.reference else None
