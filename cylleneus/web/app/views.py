from pathlib import Path

import settings
from corpus import Corpus
from index import Indexer
from cylleneus.web.display import as_html
from engine import index as ix
from flask import render_template, request
from search import Searcher
from .db import db, Search, SearchResult
from .server import app
from utils import dtformat

corpora = []
for path in Path(settings.ROOT_DIR + '/index/').iterdir():
    if path.is_dir() and ix.exists_in(str(path)):
        corpora.append(path.name)


def import_text(author, title, text):
    kwargs = {
        'author': author,
        'title': title,
    }

    indexer = Indexer(Corpus('imported'))
    n = indexer.index.doc_count_all()
    indexer.adds(text, **kwargs)

    ndocs = indexer.index.doc_count_all()
    if ndocs > n:
        success = True
    else:
        success = False
    return success

# TODO: add pagination
def search_request(corpus, query):
    search = Searcher(Corpus(corpus)).search(query)

    if search.results:
        return search


@app.route('/')
def index():
    db.connect()
    history = []
    for h in Search.select():
        history.append(h)
    db.close()

    response = {
        'version': settings.__version__,
        'corpora': corpora,
        'history': history,
    }
    return render_template('index.html', **response)


@app.route('/corpus', methods=['GET'])
def corpus():
    indexers = []
    for path in Path(settings.ROOT_DIR + '/index/').iterdir():
        if path.is_dir() and ix.exists_in(str(path)):
            indexers.append(Indexer(Corpus(path.name)))

        response = {
            'indexers': indexers,
            'corpora': corpora
        }
    return render_template('corpus.html', **response)


@app.route('/import', methods=['POST', 'GET'])
def _import():
    form = request.form
    print(form)
    author = form.get('author', None)
    title = form.get('title', None)
    filename = form.get('filename', None)
    content = form.get('content', None)

    if filename is not None and content is not None:
        success = import_text(author, title, content)
    else:
        success = False

    response = {
            'filename': filename if filename else "",
            'author': author if author else "",
            'title': title if title else "",
            'content': content if content else "",
            'success': success
        }
    return render_template('import.html', **response)


@app.route('/history', methods=['GET'])
def history():
    db.connect()
    history = []
    for h in Search.select():
        history.append(h)
    db.close()

    kwargs = request.args
    id = kwargs.get('id')
    db.connect()
    s = Search.get_by_id(id)
    db.close()

    results = [r.html for r in SearchResult.select().where(SearchResult.search == s)]

    response = {
        'version': settings.__version__,
        'corpus': s.corpus,
        'corpora': corpora,
        'query': s.query,
        'history': history,
        'results': results,
        'count': len(s.results),
    }
    return render_template('index.html', **response)


@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        form = request.form
    else:
        form = request.args

    corpora = []
    for path in Path(settings.ROOT_DIR + '/index/').iterdir():
        if path.is_dir() and ix.exists_in(str(path)):
            corpora.append(path.name)

    corpus = form.get('corpus')
    query = form.get('query')

    results = search_request(corpus, query)

    if results:
        db.connect()
        s = Search.create(
            query=query,
            corpus=results.corpus.name,
            docs=results.docs,
            minscore=results.minscore,
            top=results.top,
            start_time=results.start_time,
            end_time=results.end_time,
            maxchars=results.maxchars,
            surround=results.surround
        )
        s.save()
        for href in results.highlights:
            r = SearchResult.create(
                search=s,
                html=next(as_html([href,]))
            )
            r.save()
        db.close()

    db.connect()
    history = []
    for h in Search.select():
        history.append(h)
    db.close()

    response = {
        'version': settings.__version__,
        'corpus': corpus,
        'corpora': corpora,
        'query': query,
        'history': history,
        'results': as_html(results.highlights) if results else [],
        'count': results.count if results else (0, 0),
    }
    return render_template('index.html', **response)
