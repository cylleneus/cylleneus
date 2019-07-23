# -*- coding: utf-8 -*-

"""Console script for Cylleneus."""
import sys
from pathlib import Path

import click
from corpus import Corpus
from cylleneus import cylleneus
from index import Indexer
from search import CylleneusSearcher


@click.group()
def main():
    """Indexing commands for Cylleneus."""


@main.command()
def shell():
    cylleneus.repl.run()

@main.command()
@click.option('--corpus', '-c', 'corpus', required=True)
def index(corpus):
    indexer = Indexer(Corpus(corpus))
    docs = list(indexer.docs)

    if docs:
        for docnum, doc in docs:
            if 'author' in doc and 'title' in doc:
                click.echo(f"[{docnum}] {doc['author']}, {doc['title']}")
            else:
                click.echo(f"[{docnum}] {doc['filename']}")
    else:
        click.echo(f"[-] nothing indexed in '{corpus}'")


@main.command()
@click.option('--corpus', '-c', 'corpus', required=True)
def clear(corpus):
    indexer = Indexer(Corpus(corpus))
    indexer.clear()
    if indexer.index.doc_count_all() == 0:
        click.echo(f"[+] cleared '{corpus}'")
    else:
        click.echo('[-] failed')

@main.command()
@click.option('--corpus', '-c', 'corpus', required=True)
def create(corpus):
    indexer = Indexer(Corpus(corpus))
    indexer.create()
    if indexer.index:
        click.echo(f"[+] created '{corpus}'")
    else:
        click.echo('[-] failed')

@main.command()
@click.option('--corpus', '-c', 'corpus', required=True)
def destroy(corpus):
    if click.confirm(f"Are you sure?", default=False):
        indexer = Indexer(Corpus(corpus))
        indexer.destroy()
        if indexer.exists:
            click.echo('[-] failed')
        else:
            click.echo(f"[+] destroyed '{corpus}'")

@main.command()
@click.option('--corpus', '-c', 'corpus', required=True)
def optimize(corpus):
    indexer = Indexer(Corpus(corpus))
    indexer.optimize()
    click.echo(f"[+] optimized '{corpus}'")


@main.command()
@click.option('--corpus', '-c', 'corpus', required=True)
@click.option('--docnum', '-d', 'docnum', required=True)
def delete(corpus, docnum):
    indexer = Indexer(Corpus(corpus))
    indexer.delete(int(docnum))
    if docnum in [n for n, _ in indexer.docs]:
        click.echo(f'[-] failed')
    else:
        click.echo(f"[+] deleted document {docnum} of '{corpus}'")


@main.command()
@click.option('--corpus', '-c', 'corpus', required=True)
@click.option('--author', '-a', 'author')
@click.option('--title', '-t', 'title')
def deleteby(corpus, **kwargs):
    c = Corpus(corpus)

    with CylleneusSearcher(c.reader) as searcher:
        ndocs = len(searcher.documents(**kwargs))
        indexer = Indexer(c)
        indexer.delete_by(**kwargs)

        if len(searcher.documents(**kwargs)) != 0:
            click.echo(f'[-] failed')
        else:
            click.echo(f"[+] deleted {ndocs} documents from '{corpus}'")


@main.command()
@click.option('--corpus', '-c', 'corpus', required=True)
@click.option('--docnum', '-d', 'docnum', required=True)
@click.option('--path', '-p', 'path', required=True)
def update(corpus, docnum, path):
    indexer = Indexer(Corpus(corpus))
    indexer.update(docnum=docnum, path=Path(path))

    if docnum in [n for n, _ in indexer.docs]:
        click.echo(f"[+] updated document {docnum} in '{corpus}'")
    else:
        click.echo(f'[-] failed')


@main.command()
@click.option('--corpus', '-c', 'corpus', required=True)
@click.option('--author', '-a', 'author')
@click.option('--title', '-t', 'title')
@click.option('--path', '-p', 'path', required=True)
def updateby(corpus, **kwargs):
    kwargs['path'] = Path(kwargs['path'])
    c = Corpus(corpus)

    indexer = Indexer(c)
    indexer.update_by(**kwargs)

    with CylleneusSearcher(c.reader) as searcher:
        docnum = searcher.document_number(**kwargs)
        if docnum:
            click.echo(f"[+] updated document {docnum} in '{corpus}'")
        else:
            click.echo(f'[-] failed')


@main.command()
@click.option('--corpus', '-c', 'corpus', required=True)
@click.option('--path', '-p', 'path', required=True)
@click.option('--author', '-a', 'author')
@click.option('--title', '-t', 'title')
def add(corpus, path, **kwargs):
    indexer = Indexer(Corpus(corpus))
    n = indexer.index.doc_count_all()
    indexer.add(Path(path), **kwargs)

    ndocs = indexer.index.doc_count_all()
    if ndocs > n:
        click.echo(f"[+] added {ndocs-n} document{'s' if ndocs-n > 1 else ''} to '{corpus}'")
    else:
        click.echo('[-] failed')


@main.command()
@click.option('--corpus', '-c', 'corpus', required=True)
@click.option('--field', '-f', 'fieldname', required=True)
def lexicon(corpus, fieldname):
    c = Corpus(corpus)

    if c.index:
        with CylleneusSearcher(c.reader) as searcher:
            lex = list(searcher.lexicon(fieldname))
            click.echo(f"[+] lexicon '{fieldname}' of '{corpus}': {len(lex)} items")
            click.echo_via_pager('\n'.join([str(i) for i in lex]))
    else:
        click.echo(f'[-] failed')


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
