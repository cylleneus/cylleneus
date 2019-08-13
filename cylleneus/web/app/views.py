from pathlib import Path

import settings
from corpus import Corpus
from display import as_html
from engine import index as ix
from flask import render_template, request
from search import Searcher

from .server import app


# TODO: add pagination
def search_request(corpus, query):
    search = Searcher(Corpus(corpus)).search(query)

    if search.results:
        return search


@app.route('/')
def index():
    corpora = []
    for path in Path(settings.ROOT_DIR + '/index/').iterdir():
        if path.is_dir() and ix.exists_in(str(path)):
            corpora.append(path.name)
    response = {
        'version': settings.__version__,
        'corpora': corpora,
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
