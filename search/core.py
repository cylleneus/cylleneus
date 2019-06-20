import textwrap
from datetime import datetime

from MyCapytain.common.constants import Mimetypes
from MyCapytain.resolvers.cts.api import HttpCtsResolver
from MyCapytain.retrievers.cts5 import HttpCtsRetriever as CTS
from requests.exceptions import HTTPError

from corpus.core import Corpus
from engine.highlight import CylleneusBasicFragmentScorer, CylleneusPinpointFragmenter, \
    CylleneusUppercaseFormatter
from engine.qparser.default import CylleneusQueryParser
from engine.query.qcore import Query
from engine.searching import CylleneusSearcher


class Searcher:
    def __init__(self, corpus: Corpus):
        self._searches = []
        self._corpus = corpus

    @property
    def corpus(self):
        return self._corpus

    @corpus.setter
    def corpus(self, c):
        self._corpus = c

    # TODO: Add concurrency
    def search(self, param: str, corpus=None, debug=False):
        """ Execute the specified search parameters """

        if param:
            parser = CylleneusQueryParser("form", self.corpus.schema)
            query = parser.parse(param, debug=debug)
            search = Search(query, self.corpus)
            matches, docs = search.exec()
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
    def __init__(self, query: Query, corpus: Corpus):
        self._query = query
        self._corpus = corpus

        self._start_time = None
        self._end_time = None
        self._results = None

    @property
    def results(self):
        if self._results is None and self.query:
            self.exec()
        return self._results

    # TODO: Resolve text from external sources rather than index,
    #   regardless of corpus type, except raw text corpora
    @property
    def highlights(self):
        if self.results:
            current_hit = ''
            fragment_counter = 1
            for hit, meta, fragment in self.results:
                if meta and meta.get('meta', False):
                    divs = meta['meta'].split('-')
                else:
                    divs = []

                # For corpora without 'content', use urn to
                # resolve the text from an external CTS server
                # or load text from local file
                if 'content' not in hit:
                    if 'urn' in hit:
                        resolver = HttpCtsResolver(CTS("http://scaife-cts.perseus.org/api/cts"))

                        # TODO: Retrieve multi-line, extended passages using
                        #   'start' and 'end'
                        urn = hit.get('urn', None)
                        ref = '.'.join([meta['start'][div]
                                        for div in meta['meta'].split('-')
                                        if div != 'line'
                                        ]).replace('t1', '')
                        try:
                            passage = resolver.getTextualNode(urn, subreference=ref)
                        except HTTPError:
                            fragment = "can't resolve url!"
                        else:
                            fragment = passage.export(Mimetypes.PLAINTEXT)
                    elif 'filename' in hit:
                        filename = hit['filename']
                        work = self.corpus.load(filename)
                        fragment = work.get(meta['start'], meta['end'])
                if current_hit != hit['title']:
                    yield '\n'
                    if hit.get('author', False):
                        yield f"{hit['author'].upper()}, {hit['title'].upper()}\n"
                    else:
                        yield f"{hit['title'].upper()}\n"
                    current_hit = hit['title']
                    fragment_counter = 1
                if hit.get('meta', False):
                    start = ', '.join([f"{item}: {meta['start'][item]}" for item in meta['start'] if item in
                                       divs])
                    end = ', '.join([f"{item}: {meta['end'][item]}" for item in meta['end'] if item in divs])
                    ref = '-'.join([start, end]) if end != start else start
                else:
                    ref = fragment_counter

                yield f"{ref}\n"
                if fragment:
                    for line in textwrap.wrap(fragment, width=70):
                        yield f"    {line}\n"
                    yield '\n'
                fragment_counter += 1

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

    def exec(self):
        self.start_time = datetime.now()
        with CylleneusSearcher(self.corpus.reader) as searcher:
            results = searcher.search(self.query, terms=True, limit=None)

            self.results = []
            if results:
                results.fragmenter = CylleneusPinpointFragmenter(autotrim=True, maxchars=50, surround=100)
                results.fragmenter.charlimit = None
                results.formatter = CylleneusUppercaseFormatter(between='\nEOF\n')
                results.scorer = CylleneusBasicFragmentScorer()

                for hit in sorted(results, key=lambda x: (x['author'], x['title'])):
                    highlights = list(hit.highlights('content', top=10000000))

                    # TODO: Sort results based on meta values
                    for meta, fragment in highlights:
                        if 'content' in hit:
                            self.results.append((hit, meta, '\n'.join(textwrap.wrap(fragment, width=70))))
                        else:
                            self.results.append((hit, meta, None))
        self.end_time = datetime.now()
        return self.count

    def __str__(self):
        return f"{self.query}, {self.count} results ({self.start_time})"
