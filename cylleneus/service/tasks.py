from pathlib import Path

from celery import Celery

from cylleneus.corpus import Corpus, Work
from cylleneus.search import Searcher, Collection

# Create the app and set the broker location
Cylleneus = Celery(
    "cylleneus", backend="redis://localhost", broker="pyamqp://guest@localhost//",
)


@Cylleneus.task
def search(q, collection=None):
    if collection:
        c = Collection(
            [Corpus(work.corpus).work_by_docix(work.docix) for work in collection]
        )
    else:
        c = Collection(Corpus("perseus").works)
    searcher = Searcher(c)
    s = searcher.search(q)
    return s.to_json()


@Cylleneus.task
def corpus(c):
    return [
        {"docix": work.docix, "author": work.author, "title": work.title}
        for work in Corpus(c).works
    ]


@Cylleneus.task
def index(corpus, filename, author=None, title=None):
    c = Corpus(corpus)

    w = Work(c, author, title)
    docix = w.indexer.from_file(Path(filename))

    return {
        "corpus":   corpus,
        "docix":    docix,
        "filename": filename,
        "author":   w.author,
        "title":    w.title,
    }
