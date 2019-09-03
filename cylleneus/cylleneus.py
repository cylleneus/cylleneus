# -*- coding: utf-8 -*-

"""Main module."""


import codecs
import re
import sys
from pathlib import Path

import parawrap
import settings
from corpus import Corpus, Work
from riposte import Riposte
from riposte.printer import Palette
from search import Searcher, Collection
from utils import slugify

_collection = None
_searcher = Searcher(_collection)
_corpus = None
_search = None


BANNER = r"""
  ____      _ _                           
 / ___|   _| | | ___ _ __   ___ _   _ ___ 
| |  | | | | | |/ _ \ '_ \ / _ \ | | / __|
| |__| |_| | | |  __/ | | |  __/ |_| \__ \
 \____\__, |_|_|\___|_| |_|\___|\__,_|___/
      |___/                         
Next-gen corpus search for Greek and Latin
"""


class CustomRiposte(Riposte):
    @property
    def prompt(self):
        if _collection and _collection.count > 0:
            return f"cylleneus ({_collection.count} documents):~ $ "
        else:
            return self._prompt  # reference to `prompt` parameter.


# TODO: add posix switch in Riposte for raw argument parsing
repl = CustomRiposte(
    prompt='cylleneus:~ $ ',
    banner=BANNER,
    # posix=False
)


@repl.command("search")
def search(*args):
    global _searcher, _search, _collection

    if _collection is not None and _collection.works:
        query = ' '.join(args)
        _searcher.collection = _collection
        _search = _searcher.search(query)

        if _search is not None:
            if len(_search.results) > 0:
                repl.success(f"{_search.spec}: {_search.time} secs, {_search.count[0]} matches")
            else:
                repl.error(f"{_search.spec}: {_search.time} secs, nothing found")
    else:
        repl.error(f"no search collection")

@repl.command("credits")
def credits():
    repl.info(
        Palette.BLUE.format(f"Cylleneus v{settings.__version__}: Next-gen corpus search for Greek and Latin"),
        Palette.GREY.format("(c) 2019 William Michael Short")
    )


@repl.command("select")
def select(docixs: list=None):
    global _collection, _corpus

    if not _collection:
        _collection = Collection()

    if docixs and isinstance(docixs, list):
        if _corpus:
            ndocs = _collection.count
            for docix in docixs:
                _collection.add(_corpus.work_by_docix(docix))
            n = _collection.count - ndocs
            if n:
                repl.success(f"added {n} documents to collection")
        else:
            repl.error(f"no corpus selected")
    else:
        repl.info(Palette.BOLD.format(f"{_collection.count} documents selected"))

        for i, work in enumerate(_collection):
            repl.info(Palette.GREY.format(f"[{i + 1}] {work.doc['author'].title()},"
                                              f" {work.doc['title'].title()} [{work.corpus.name}]"))


@repl.command("unselect")
def unselect(docixs: list=None):
    global _collection, _corpus

    if _collection:
        n = _collection.count
        if docixs and isinstance(docixs, list):
            for ix in docixs:
                _collection.works.pop(ix - 1)
        if n - _collection.count > 0:
            repl.success(f"removed {n - _collection.count} documents from collection")
    else:
        repl.error(f"no search collection")

@repl.command("index")
def index():
    global _corpus

    if _corpus:
        repl.info(Palette.BOLD.format(f"corpus '{_corpus.name}', {_corpus.doc_count_all} documents indexed"))
        for docix, doc in _corpus.iter_docs():
            repl.info(Palette.GREY.format(f"{docix}. {doc['author'].title()}, {doc['title'].title()}"))
    else:
        repl.error("no corpus selected")

@repl.command("select-by")
def selectby(author: str ='*', title: str = '*'):
    global _corpus, _collection

    ndocs = _collection.count
    for ix in _corpus.indices_for(slugify(author), slugify(title)):
        for docix in list(ix.reader().all_doc_nums()):
            _collection.add(_corpus.work_by_docix(docix))

    if _collection.count > ndocs:
        repl.success(f"added {_collection.count - ndocs} documents to collection")


@repl.command("select-all")
def selectall():
    global _collection, _corpus

    if not _collection:
        _collection = Collection()

    if _corpus:
        ndocs = _collection.count
        for work in _corpus.works:
            _collection.add(work)

        if _collection.count > ndocs:
            repl.success(f"added {_collection.count - ndocs} documents to collection")
    else:
        repl.error(f"no corpus selected")

@repl.command("unselect-all")
def unselectall():
    global _collection

    if not _collection:
        _collection = Collection()

    ndocs = _collection.count
    _collection.works = []

    if _collection.count == 0:
        repl.success(f"removed {ndocs} documents from collection")


@repl.command("corpus")
def corpus(corpus_name: str = None):
    global _corpus, _searcher, _search

    if corpus_name:
        if not _corpus or corpus_name != _corpus.name:
            _corpus = Corpus(corpus_name)
            _searcher.corpus = _corpus
            _searcher._docs = None
            repl.success(f"'{_corpus.name}', {_corpus.doc_count_all} docs")
    else:
        for path in Path(settings.ROOT_DIR + '/corpus/').glob('*'):
            if path.is_dir():
                repl.success(
                    Palette.GREEN.format(
                        f"'{path.name}'"
                    )
                )


@repl.command("save")
def save(n: int = None, filename: str = None):
    global _searcher, _search

    if n:
        target = _searcher.history[n-1]
    else:
        target = _search
    if not filename:
        filename = slugify(target.query, allow_unicode=False)

    if target.results:
        with codecs.open(f"{filename}.txt", "w", "utf8") as fp:
            for corpus, author, title, urn, reference, text in target.to_text():
                fp.write(f"{author}, {title} [{corpus}] [{urn}] {reference}\n{text}\n\n")
            repl.success(
                "saved:",
                Palette.WHITE.format(
                        f"'{filename}.txt'"
                )
            )
    else:
        repl.error("nothing to save")


@repl.command("display")
def display(n: int = None):
    global _searcher, _search

    if n:
        target = _searcher.history[n-1]
    else:
        target = _search

    if target.results:
        ctitle = None

        for href in target.highlights:
            if ctitle != href.title:
                repl.success(Palette.BOLD.format(f"{href.author}, {href.title} [{href.corpus}]"))
                ctitle = href.title
            repl.info(Palette.GREY.format(f"{href.reference}:"))

            if href.text:
                # Process pre-match context
                text = re.sub(
                    r"<pre>(.*?)</pre>",
                    r"\1",
                    href.text,
                    flags=re.DOTALL
                )
                # Process post-match context
                text = re.sub(
                    r"<post>(.*?)</post>",
                    r"\1",
                    text,
                    flags=re.DOTALL
                )
                # Process matched text
                text = re.sub(
                    r"<match>(.*?)</match>",
                    r"\1",
                    text,
                    flags=re.DOTALL
                )
                # Highlight pinpointed text
                text = re.sub(
                    r"<em>(.*?)</em>",
                    Palette.CYAN.format(r"\1"),
                    text,
                    flags=re.DOTALL
                )
                for line in parawrap.wrap(text):
                    if line:
                        repl.print(line)
            repl.print()
    else:
        repl.error("no results")


@repl.command("history")
def history():
    global _searcher, _search

    for i, s in enumerate(_searcher.history):
        hits, docs, corpora = s.count
        repl.print(
            Palette.YELLOW.format(f"[{i + 1}]"),
            Palette.WHITE.format(f"{s.spec}"),
            Palette.BOLD.format(f"{hits} results in {docs} docs in {corpora} corpora")
        )


@repl.command("quit")
def quit():
    sys.exit()


@repl.command("help")
def help():
    repl.print(Palette.CYAN.format("Available commands:"))
    repl.info('''    search <query>              execute a query over the current corpus              
    history                     list search history
    save [<#>] [<filename>]     save search results to disk
    display [<#>]               display search results
    corpus [<name>]             load corpus index by name
    select                      list currently selected documents for searching
    select "[1,2...]"           select documents from current corpus for searching
    unselect "[1,2...]"         unselect documents for searching
    select-all                  select all docs of current corpus for searching
    unselect-all                unselect all documents for searching''')

if __name__ == "__main__":
    sys.exit(repl.run())
