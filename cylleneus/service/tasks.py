from celery import Celery

from corpus import Corpus
from search import Searcher, Collection

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
def index(corpus):
    return [
        {"docix": work.docix, "author": work.author, "title": work.title}
        for work in Corpus(corpus).works
    ]
