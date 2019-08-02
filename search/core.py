from datetime import datetime

import config
from corpus.core import Corpus
from engine.highlight import CylleneusBasicFragmentScorer, CylleneusDefaultFormatter, CylleneusPinpointFragmenter
from engine.qparser.default import CylleneusQueryParser
from engine.query.qcore import Query
from engine.searching import CylleneusSearcher


class Searcher:
    def __init__(self, corpus: Corpus, doc_ids: list = None):
        self._searches = []
        self._corpus = corpus
        self._docs = set(doc_ids) if doc_ids else None

    @property
    def corpus(self):
        return self._corpus

    @corpus.setter
    def corpus(self, c):
        self._corpus = c

    @property
    def docs(self):
        if self._docs is None:
            return set(self.corpus.reader.all_doc_ids())
        else:
            return set(self._docs)

    @docs.setter
    def docs(self, doc_ids: list):
        self._docs = set(doc_ids)

    def search(self, param: str, corpus=None, doc_ids: list = None, minscore=None, debug=config.DEBUG):
        """ Execute the specified search parameters """

        if param:
            parser = CylleneusQueryParser("form", self.corpus.schema)
            query = parser.parse(param, debug=debug)
            if not corpus:
                corpus = self.corpus
            if not doc_ids:
                doc_ids = self.docs
            search = Search(param, query, corpus, doc_ids=doc_ids, minscore=minscore)
            matches, docs = search.run()
            if matches > 0:
                self.searches.append(search)
            return search

    @property
    def searches(self):
        return self._searches

    @property
    def history(self):
        return self.searches


class Search:
    def __init__(self, param: str, query: Query, corpus: Corpus, doc_ids: list = None, top=None, minscore=None):
        self._param = param
        self._query = query
        self._corpus = corpus
        self._docs = set(doc_ids) if doc_ids else None
        self._minscore = minscore
        self._top = top

        self._start_time = None
        self._end_time = None
        self._results = None

        self._maxchars = 70     # width of one line
        self._surround = 70 if 70 > config.CHARS_OF_CONTEXT else config.CHARS_OF_CONTEXT

    @property
    def docs(self):
        return self._docs

    @property
    def maxchars(self):
        return self._maxchars

    @maxchars.setter
    def maxchars(self, n):
        self._results = n

    @property
    def surround(self):
        return self._surround

    @surround.setter
    def surround(self, n):
        self._surround = n


    @property
    def results(self):
        if self._results is None and self.query:
            self.run()
        return self._results

    @property
    def highlights(self):
        if self.results:
            for hit, meta, fragment in self.results:
                author, title, reference, text = self.corpus.fetch(hit, meta, fragment)
                yield author, title, reference, text

    @property
    def param(self):
        return self._param

    @property
    def corpus(self):
        return self._corpus

    @results.setter
    def results(self, r):
        self._results = r

    @property
    def query(self):
        return self._query

    @property
    def start_time(self):
        return self._start_time

    @start_time.setter
    def start_time(self, t):
        self._start_time = t

    @property
    def end_time(self):
        return self._end_time

    @end_time.setter
    def end_time(self, t):
        self._end_time = t

    @property
    def time(self):
        return self.end_time - self.start_time

    @property
    def count(self):
        if self.results and len(self.results) > 0:
            docs = len(set([hit.docnum for hit, _, _ in self.results]))
            matches = len(self.results)
            return matches, docs
        else:
            return 0, 0

    @property
    def minscore(self):
        return self._minscore

    @property
    def top(self):
        return self._top

    def run(self):
        self.start_time = datetime.now()
        with CylleneusSearcher(self.corpus.reader) as searcher:
            results = searcher.search(self.query, terms=True, limit=None, filter=self.docs)

            self.results = []
            if results:
                results.fragmenter = CylleneusPinpointFragmenter(
                    autotrim=True,
                    charlimit=None,
                    maxchars=self.maxchars,
                    surround=self.surround
                )
                results.scorer = CylleneusBasicFragmentScorer()
                results.formatter = CylleneusDefaultFormatter()
                for hit in sorted(results, key=lambda x: (x['author'], x['title'])):
                    self.results.extend(
                        hit.highlights(
                            fieldname='content',
                            top=self.top,
                            minscore=self.minscore
                        )
                    )

        self.end_time = datetime.now()
        return self.count

    def __repr__(self):
        return f"Search(query={self.query}, corpus={self.corpus}, results={self.count})"

    def __str__(self):
        return self.param
