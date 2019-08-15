# -*- coding: utf-8 -*-

"""Main module."""


import codecs
import re
import sys
from pathlib import Path

import parawrap
import settings
from corpus import Corpus
from engine import index
from riposte import Riposte
from riposte.printer import Palette
from search import Searcher
from utils import slugify

_corpus = Corpus('lasla')
_searcher = Searcher(_corpus)
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
        if _corpus:
            return f"cylleneus ({_corpus.name}):~ $ "
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
    global _searcher, _search

    query = ' '.join(args)
    _search = _searcher.search(query)

    if _search.results:
       repl.success(f"{_search.param}: {_search.time} secs, {_search.count[0]} matches")
    else:
       repl.error(f"{_search.param}: {_search.time} secs, nothing found")


@repl.command("credits")
def credits():
    repl.info(
        Palette.BLUE.format(f"Cylleneus v{settings.__version__}: Next-gen corpus search for Greek and Latin"),
        Palette.GREY.format("(c) 2019 William Michael Short")
    )


@repl.command("select")
def select(doc_ids: list = None):
    global _searcher

    if doc_ids:
        _searcher.docs = doc_ids
    else:
        repl.info(Palette.WHITE.format(f"corpus '{_corpus.name}', {_corpus.indexer.doc_count_all} documents indexed"))
        for docnum, fields in _corpus.indexer.iter_docs():
            if docnum in _searcher.docs:
                repl.info(Palette.BOLD.format(f"{docnum}. {fields['author'].title()}, {fields['title'].title()}"))
            else:
                repl.info(Palette.GREY.format(f"{docnum}. {fields['author'].title()}, {fields['title'].title()}"))


@repl.command("selectby")
def selectby(author: str = None, title: str = None):
    global _corpus, _searcher

    kwargs = {}
    if author:
        kwargs['author'] = author
    if title:
        kwargs['title'] = title

    if 'author' in _corpus.schema and 'title' in _corpus.schema:
        _searcher.docs = [doc['docix'] for doc in _corpus.index.searcher().documents(**kwargs)]


@repl.command("corpus")
def corpus(corpus_name: str = None):
    global _corpus, _searcher, _search

    if corpus_name:
        _corpus = Corpus(corpus_name)
        _searcher.corpus = _corpus
        repl.success(f"'{_corpus.name}', {_corpus.indexer.doc_count_all} docs")
    else:
        for path in Path(settings.ROOT_DIR + '/index/').iterdir():
            if path.is_dir() and index.exists_in(str(path)):
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
            for author, title, urn, reference, text in target.to_text():
                fp.write(f"{author}, {title} [{urn}] {reference}\n{text}\n\n")
            repl.success(f"saved: '{filename}.txt'")
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
                repl.success(Palette.BOLD.format(f"{href.author}, {href.title}"))
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

    for i, search in enumerate(_searcher.history):
        hits, docs = search.count
        repl.print(
            Palette.YELLOW.format(f"[{i + 1}]"),
            Palette.WHITE.format(f"{search.query} ['{search.corpus}']"),
            Palette.BOLD.format(f"{hits} matches in {docs} docs")
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
    select ["[1, 2...]"]        select documents or list currently selected''')


if __name__ == "__main__":
    sys.exit(repl.run())
