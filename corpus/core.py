import settings
from pathlib import Path
from . import indexer
from . import lasla, latin_library, perseus


class Corpus:
    def __init__(self, name: str):
        self._name = name
        self._indexer = indexer.Indexer(self)

    @property
    def name(self):
        return self._name

    @property
    def indexer(self):
        return self._indexer

    @property
    def indices(self):
        return self.indexer.indices

    def indices_for(self, author: str = None, title: str = None):
        if author and title:
            ixs = self.indexer.indices_for(author, title)
        elif author:
            ixs = self.indexer.indices_for(author=author)
        else:
            ixs = self.indexer.indices_for(title=title)
        return ixs


    @property
    def is_searchable(self):
        return self.indexer.schema and self.indexer.indices

    @property
    def readers(self):
        return [ix.reader() for ix in self.indices]

    def readers_for(self, author: str='*', title: str='*'):
        return [ix.reader() for ix in self.indices_for(author, title)]

    def reader_for_docnum(self, docnum: int):
        for reader in self.readers:
            ids = list(reader.all_doc_nums())
            if docnum in ids:
                return reader

    @property
    def path(self):
        return Path(f"{settings.ROOT_DIR}/corpus/{self.name}")

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
