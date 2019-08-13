from pathlib import Path

import settings
from corpus import Corpus
from index import Indexer
from cylleneus.web.display import as_html
from engine import index as ix
from flask import render_template, request
from search import Searcher

from .server import app


corpora = []
for path in Path(settings.ROOT_DIR + '/index/').iterdir():
    if path.is_dir() and ix.exists_in(str(path)):
        corpora.append(path.name)


def import_text(author, title, file, text):
    kwargs = {
        'author': author,
        'title': title,
        'file': file,
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
    response = {
        'version': settings.__version__,
        'corpora': corpora,
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
    if request.method == 'POST':
        form = request.form
    else:
        form = request.args

    author = form.get('author', None)
    title = form.get('title', None)
    file = form.get('filename', None)
    text = form.get('text', None)

    if file is not None and text is not None:
        success = import_text(author, title, file, text)
    else:
        success = False

    response = {
            'path': file if file else "",
            'author': author if author else "",
            'title': title if title else "",
            'text': text if text else "",
            'success': success
        }
    return render_template('import.html', **response)


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

    response = {
        'version': settings.__version__,
        'title': query,
        'corpus': corpus,
        'corpora': corpora,
        'query': query,
        'results': as_html(results.highlights),
        'count': results.count,
    }
    return render_template('index.html', **response)
