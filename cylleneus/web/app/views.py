from pathlib import Path
import json

from flask import render_template, request

import settings
from cylleneus import __version__
from corpus import Corpus, Work
from search import Searcher, Collection

from .db import Search, SearchResult, db
from .display import as_html
from .server import app

_corpora = []
for path in Path(settings.ROOT_DIR + '/corpus').glob('*'):
    if path.is_dir() and Path(path / 'index').exists():
        _corpora.append(path.name)


def import_text(corpus, author, title, filename, content):
    kwargs = {
        'corpus': corpus,
        'author': author,
        'title': title,
        'filename': filename,
    }

    try:
        c = Corpus(corpus)
        w = Work(c, author=author, title=title)
        ndocs = c.doc_count_all
        w.indexer.from_string(content=content, **kwargs)

        if c.doc_count_all > ndocs:
            success = True
        else:
            success = False
    except Exception as e:
        success = False
    return success


# TODO: add pagination
def search_request(collection, query):
    c = Collection(collection)
    search = Searcher(c).search(query)

    if search.results:
        return search


@app.route('/', methods=['GET', 'POST'])
def index():
    form = request.form
    collection = form.get('collection', None)

    works = []
    if collection:
        ids = json.loads(collection)
        for id in ids:
            corpus, n = id.split(',')
            c = Corpus(corpus)
            w = c.work_by_docix(int(n))
            works.append(w)

    db.connect()
    history = []
    for h in Search.select():
        history.append(h)
    db.close()

    response = {
        'version': __version__,
        'corpora': _corpora,
        'works': works,
        'collection': collection,
        'history': history
    }
    return render_template('index.html', **response)


@app.route('/collection', methods=['GET'])
def collection():
    response = {
            'corpora': [Corpus(corpus) for corpus in _corpora]
    }
    return render_template('collection.html', **response)


@app.route('/import', methods=['POST', 'GET'])
def _import():
    form = request.form

    corpus = form.get('corpus', None)
    author = form.get('author', None)
    title = form.get('title', None)
    filename = form.get('filename', None)
    content = form.get('content', None)

    if filename is not None and content is not None:
        success = import_text(corpus, author, title, filename, content)
    else:
        success = False

    response = {
            'filename': filename if filename else "Choose file...",
            'corpus': corpus if corpus else "",
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

    works = []
    ids = json.loads(s.collection)
    for id in ids:
        corpus, n = id.split(',')
        c = Corpus(corpus)
        w = c.work_by_docix(int(n))
        works.append(w)

    results = [r.html for r in SearchResult.select().where(SearchResult.search == s)]

    response = {
        'version': __version__,
        'collection': s.collection,
        'works': works,
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

    collection = form.get('collection')
    query = form.get('query')

    works = []
    ids = json.loads(collection)
    for id in ids:
        corpus, n = id.split(',')
        c = Corpus(corpus)
        w = c.work_by_docix(int(n))
        works.append(w)

    results = search_request(works, query)

    if results:
        db.connect()
        try:
            s = Search.get(query=query, collection=collection),
        except Search.DoesNotExist:
            names = [f"{work.author}, {work.title}" for work in works]
            s = Search.create(
                query=query,
                collection=collection,
                prettified=f"{'; '.join(names)}",
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
        'version': __version__,
        'collection': collection,
        'works': works,
        'corpora': _corpora,
        'query': query,
        'history': history,
        'results': as_html(results.highlights) if results else [],
        'count': results.count if results else (0, 0),
    }
    return render_template('index.html', **response)
