import codecs
import json
from pathlib import Path

import config
from MyCapytain.common.constants import Mimetypes
from MyCapytain.resolvers.cts.api import HttpCtsResolver
from MyCapytain.retrievers.cts5 import HttpCtsRetriever as CTS
from engine import fields, index
from requests.exceptions import HTTPError


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
        """ Fetch corpus data for a given match in a document
        :param: hit         The hit object, representing a specific author's work
                            or part of it
        :param: meta        Meta data for citation referencing
        :param: fragment    Text fragment, only for raw plaintext corpora
        :returns:           author, title, reference, text
        """

        if 'content' not in hit:
            if 'urn' in hit:
                # TODO: move to Work
                resolver = HttpCtsResolver(CTS("http://scaife-cts.perseus.org/api/cts"))

                # TODO: Retrieve multi-line, extended passages using
                #   'start' and 'end' with variable context
                urn = hit.get('urn', None)
                if 'line' in meta['meta'] and len(meta['meta'].split('-')) <= 2:
                    cite = '.'.join([meta['start'][div]
                                    for div in meta['meta'].split('-')
                                    ]).replace('t1', '')
                else:
                    cite = '.'.join([meta['start'][div]
                                    for div in meta['meta'].split('-')
                                    if div != 'line'
                                    ]).replace('t1', '')
                try:
                    passage = resolver.getTextualNode(urn, subreference=cite)
                except HTTPError:
                    text = None
                else:
                    text = passage.export(Mimetypes.PLAINTEXT)
            elif 'filename' in hit:
                filename = hit['filename']
                work = self.load(filename)
                text = work.get(meta['start'], meta['end'])
        else:
            text = fragment

        if meta and meta.get('meta', False):
            divs = meta['meta'].split('-')
        else:
            divs = []
        if hit.get('meta', False):
            start = ', '.join([f"{item}: {meta['start'][item]}" for item in meta['start'] if item in
                               divs])
            end = ', '.join([f"{item}: {meta['end'][item]}" for item in meta['end'] if item in divs])
            reference = '-'.join([start, end]) if end != start else start
        else:
            reference = None

        if hit.get('author', False):
            author = hit['author']
        else:
            author = None

        if hit.get('title', False):
            title = hit['title']
        else:
            title = None

        return author, title, reference, text

    def load(self, filename):
        if self.name == 'perseus':
            filename = Path(filename).name
            with codecs.open(config.ROOT_DIR + f'/corpus/text/perseus/{filename}', 'r', 'utf8') as fp:
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
