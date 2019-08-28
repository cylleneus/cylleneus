from pathlib import Path
import json

import settings
from corpus import Corpus, Work
from flask import render_template, request
from search import Searcher, Collection

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
        c = Corpus('imported')
        w = Work(c, author=author, title=title)
        ndocs = c.doc_count_all
        w.indexer.from_string(content, **kwargs)

        if ndocs > c.doc_count_all:
            success = True
        else:
            success = False
    except Exception as e:
        success = False
    return success


# TODO: add pagination
def search_request(corpus, query):
    c = Corpus(corpus)
    collection = Collection(list(c.works))
    search = Searcher(collection).search(query)

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
    response = {
            'corpora': [Corpus(corpus) for corpus in _corpora]
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
        'collection': s.collection,
        'corpora': _corpora,
        'corpus': s.corpus,
        'query': s.query,
        'history': history,
        'results': results,
        'count': len(s.results),
    }
    return render_template('index.html', **response)

# TODO: implement collections
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
            s = Search.get(query=query, collection=str(results.collection))
        except Search.DoesNotExist:
            s = Search.create(
                query=query,
                corpus=corpus,
                collection=json.dumps(str(results.collection)),
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
