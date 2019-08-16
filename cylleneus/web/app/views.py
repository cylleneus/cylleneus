from pathlib import Path

import settings
from corpus import Corpus, Indexer
from engine import index as ix
from flask import render_template, request
from search import Searcher

from .db import Search, SearchResult, db
from .display import as_html
from .server import app

_corpora = []
for path in Path(settings.ROOT_DIR + '/corpus').glob('*'):
    if path.is_dir() and Path(path / 'index').exists():
        _corpora.append(path.name)


def import_text(author, title, filename, content):
    kwargs = {
        'author': author,
        'title': title,
        'filename': filename,
    }

    try:
        indexer = Indexer(Corpus('imported'))
        n = indexer.doc_count_all
        indexer.adds(content, **kwargs)

        ndocs = indexer.doc_count_all
        if ndocs > n:
            success = True
        else:
            success = False
    except Exception as e:
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
        'corpora': _corpora,
        'history': history,
    }
    return render_template('index.html', **response)


@app.route('/corpora', methods=['GET'])
def corpora():
    indexers = []
    for path in Path(settings.ROOT_DIR + '/corpus/').glob('*'):
        if path.is_dir() and Path(path / 'index').exists():
            indexers.append(Indexer(Corpus(path.name)))

        response = {
            'indexers': indexers,
            'corpora': _corpora
        }
    return render_template('corpora.html', **response)


@app.route('/import', methods=['POST', 'GET'])
def _import():
    form = request.form

    author = form.get('author', None)
    title = form.get('title', None)
    filename = form.get('filename', None)
    content = form.get('content', None)

    if filename is not None and content is not None:
        success = import_text(author, title, filename, content)
    else:
        success = False

    response = {
            'filename': filename if filename else "Choose file...",
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
        'corpora': _corpora,
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

    corpus = form.get('corpus')
    query = form.get('query')

    results = search_request(corpus, query)

    if results:
        db.connect()
        try:
            s = Search.get(query=query, corpus=results.corpus.name)
        except Search.DoesNotExist:
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
        finally:
            for href in results.highlights:
                r = SearchResult.get_or_create(
                    search=s,
                    html=next(as_html([href,]))
                )
                if r[1]:
                    r[0].save()
        db.close()

    db.connect()
    history = []
    for h in Search.select():
        history.append(h)
    db.close()

    response = {
        'version': settings.__version__,
        'corpus': corpus,
        'corpora': _corpora,
        'query': query,
        'history': history,
        'results': as_html(results.highlights) if results else [],
        'count': results.count if results else (0, 0),
    }
    return render_template('index.html', **response)
