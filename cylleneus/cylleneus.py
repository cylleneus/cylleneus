# -*- coding: utf-8 -*-

"""Main module."""


import codecs
import re
import sys
import textwrap
import unicodedata
from pathlib import Path

import config
from corpus import Corpus
from engine import index
from riposte import Riposte
from riposte.printer import Palette
from search import Searcher

_corpus = Corpus('lasla')
_searcher = Searcher(_corpus)
_search = None


BANNER = """
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


repl = CustomRiposte(
    # banner=BANNER,
    prompt='cylleneus:~ $ '
)


@repl.command("search")
def search(query: str):
    global _searcher, _search

    _search = _searcher.search(query)
    if _search.results:
        repl.success(f"{query}: {_search.time} secs, {_search.count[0]} results")
    else:
        repl.error(f"{query}: {_search.time} secs, nothing found")


@repl.command("credits")
def credits():
    repl.info(Palette.BLUE.format("Cylleneus v0.0.1: Next-gen corpus search for Greek and Latin"))
    repl.info(Palette.GREY.format("(c) 2019 William Michael Short"))


@repl.command("select")
def select(doc_ids: list = None):
    global _searcher

    if doc_ids:
        _searcher.docs = doc_ids
    else:
        repl.info(Palette.WHITE.format(f"corpus '{_corpus.name}', {_corpus.index.doc_count_all()} indexed"))
        for docnum, fields in _corpus.index.reader().iter_docs():
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

    if corpus_name and index.exists_in(config.ROOT_DIR + f"/index/{corpus_name}"):
        _corpus = Corpus(corpus_name)
        _searcher.corpus = _corpus
        repl.success(f"corpus '{_corpus.name}', {_corpus.index.doc_count_all()} indexed")
    else:
        repl.info(Palette.GREEN.format("Available corpora: " + ", ".join(
            [f"'{path.name}'" for path in Path(config.ROOT_DIR + '/index/').iterdir()
             if path.is_dir() and index.exists_in(str(path))])))


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
            for hlite in target.highlights:
                fp.write(hlite)
            repl.success(f"saved results as '{filename}.txt'")
    else:
        repl.error("nothing to save")


@repl.command("show")
def show(n: int = None):
    global _searcher, _search

    if n:
        target = _searcher.history[n-1]
    else:
        target = _search

    if target.results:
        ctitle = None
        counter = 1
        for author, title, reference, text in target.highlights:
            if ctitle != title:
                repl.success(Palette.BOLD.format(f"{author}, {title}"))
                ctitle = title
                counter = 1
            if not reference:
                reference = counter
            repl.info(Palette.GREY.format(f"{reference}:", end=' '))

            if text:
                for line in textwrap.wrap(text.strip('\n'), width=70):
                    repl.print(Palette.WHITE.format(line))
            else:
                repl.error(f"could not resolve")
            repl.print('\n')
            counter += 1
    else:
        repl.error("no results")


@repl.command("history")
def history():
    global _searcher, _search

    for i, query in enumerate(_searcher.history):
        repl.print(f"{i + 1}.\t{query}")


@repl.command("quit")
def quit():
    sys.exit()


@repl.command("help")
def help():
    repl.print(Palette.CYAN.format("Available commands:"))
    repl.info('''    search <query>              execute a query over the current corpus              
    history                     list search history
    save [<#>] [<filename>]     save search results to disk
    show [<#>]                  show search results
    corpus [<name>]             load corpus index by name
    select ["[1, 2...]"]        select documents or list currently selected''')


def slugify(value, allow_unicode=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces to hyphens.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Convert to lowercase. Also strip leading and trailing whitespace.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '-', value)


if __name__ == "__main__":
    sys.exit(repl.run())
