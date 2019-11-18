from celery import Celery

from corpus import Corpus
from search import Searcher, Collection

# Create the app and set the broker location
Cylleneus = Celery(
    'cylleneus',
    backend='redis://localhost',
    broker='pyamqp://guest@localhost//',
)
Cylleneus.conf.broker_heartbeat = 0
Cylleneus.conf.result_persistent = True
Cylleneus.conf.worker_prefetch_multiplier = 0


@Cylleneus.task(acks_late=True)
def search(q, collection=None):
    if collection:
        c = Collection([Corpus(corpus).work_by_docix(docix) for corpus, docix in collection])
    else:
        c = Collection(Corpus("lasla").works)
    searcher = Searcher(c)
    s = searcher.search(q)
    return s.to_json()
