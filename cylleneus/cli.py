# -*- coding: utf-8 -*-

"""Console script for Cylleneus."""

import sys
from pathlib import Path

import click
import click_spinner

from corpus import Corpus, Work
from search import CylleneusSearcher


@click.group()
def main():
    """Indexing commands for Cylleneus."""


@main.command()
def shell():
    from cylleneus import cylleneus

    sys.argv = [sys.argv[0]]  # clear sys.argv to avoid pass-through
    cylleneus.repl.run()


@main.command()
def web():
    from .web.app import server
    import webbrowser

    server.run()
    webbrowser.open_new('http://127.0.0.1:5000/')

@main.command()
@click.option('--corpus', '-c', 'corpus', required=True)
def index(corpus):
    c = Corpus(corpus)
    docs = sorted(c.iter_docs(), key=lambda x: x[0])

    if docs:
        for docix, doc in docs:
            if 'author' in doc and 'title' in doc:
                click.echo(f"[{doc['docix']}] {doc['author']}, {doc['title']} [{doc['filename']}]")
            else:
                click.echo(f"[{doc['docix']}] {doc['filename']}")
    else:
        click.echo(f"[-] nothing indexed for '{corpus}'")


@main.command()
@click.option('--corpus', '-c', 'corpus', required=True)
def clear(corpus):
    with click_spinner.spinner():
        c = Corpus(corpus)
        c.clear()

    if c.doc_count_all == 0:
        click.echo(f"[+] cleared '{corpus}'")
    else:
        click.echo('[-] failed')


@main.command()
@click.option('--corpus', '-c', 'corpus', required=True)
def destroy(corpus):
    if click.confirm(f"Are you sure?", default=False):
        with click_spinner.spinner():
            c = Corpus(corpus)
            c.destroy()

        if c.is_searchable:
            click.echo('[-] failed')
        else:
            click.echo(f"[+] destroyed '{corpus}'")

@main.command()
@click.option('--corpus', '-c', 'corpus', required=True)
def optimize(corpus):
    with click_spinner.spinner():
        c = Corpus(corpus)
        c.optimize()

    click.echo(f"[+] optimized '{corpus}'")


@main.command()
@click.option('--corpus', '-c', 'corpus', required=True)
@click.option('--docix', '-d', 'docix', required=True)
def delete(corpus, docix):
    with click_spinner.spinner():
        c = Corpus(corpus)
        c.delete_by_ix(int(docix))

    if docix in list(c.all_doc_ixs()):
        click.echo(f'[-] failed')
    else:
        click.echo(f"[+] deleted document {docix} of '{corpus}'")


@main.command()
@click.option('--corpus', '-c', 'corpus', required=True)
@click.option('--author', '-a', 'author')
@click.option('--title', '-t', 'title')
def deleteby(corpus, **kwargs):
    with click_spinner.spinner():
        c = Corpus(corpus)
        pre_ndocs = c.doc_count_all
        c.delete_by()
        post_ndocs = c.doc_count_all
        ndocs = pre_ndocs - post_ndocs

    if ndocs == 0:
        click.echo(f'[-] failed')
    else:
        click.echo(f"[+] deleted {ndocs} documents from '{corpus}'")


@main.command()
@click.option('--corpus', '-c', 'corpus', required=True)
@click.option('--docix', '-d', 'docix', required=True)
@click.option('--path', '-p', 'path', required=True)
def update(corpus, docix, path):
    with click_spinner.spinner():
        c = Corpus(corpus)
        c.update(docix=docix, path=Path(path))

    if docix in [doc['docix'] for doc in c.iter_docs()]:
        click.echo(f"[+] updated document {docix} in '{corpus}'")
    else:
        click.echo(f'[-] failed')


@main.command()
@click.option('--corpus', '-c', 'corpus', required=True)
@click.option('--author', '-a', 'author')
@click.option('--title', '-t', 'title')
@click.option('--path', '-p', 'path', required=True)
def updateby(corpus, **kwargs):
    with click_spinner.spinner():
        kwargs['path'] = Path(kwargs['path'])
        c = Corpus(corpus)
        docix = c.update_by(**kwargs)

    if docix in [doc['docix'] for doc in c.docs]:
        click.echo(f"[+] updated document {docix} in '{corpus}'")
    else:
        click.echo(f'[-] failed')


@main.command()
@click.option('--corpus', '-c', 'corpus', required=True)
@click.option('--path', '-p', 'path', required=True)
@click.option('--author', '-a', 'author')
@click.option('--title', '-t', 'title')
def add(corpus, path, author, title):
    with click_spinner.spinner():
        c = Corpus(corpus)
        pre_ndocs = c.doc_count_all

        w = Work(c, author, title)
        w.indexer.from_file(Path(path))

    post_ndocs = c.doc_count_all
    ndocs = post_ndocs-pre_ndocs
    if post_ndocs > pre_ndocs:
        click.echo(f"[+] added {ndocs} document{'s' if ndocs > 1 else ''} to '{corpus}'")
    else:
        click.echo('[-] failed')


@main.command()
@click.option('--corpus', '-c', 'corpus', required=True)
@click.option('--destructive/--not-destructive', '-d/-D', default=True)
def create(corpus, destructive):
    with click_spinner.spinner():
        c = Corpus(corpus)
        if destructive:
            c.destroy()

        for file in c.text_dir.glob(c.glob):
            w = Work(corpus=c)
            _ = w.indexer.from_file(file)

        c.optimize()

    ndocs = c.doc_count_all
    if ndocs > 0:
        click.echo(f"[+] created '{corpus}' with {ndocs} document{'s' if ndocs > 1 else ''}")
    else:
        click.echo('[-] failed')


@main.command()
@click.option('--corpus', '-c', 'corpus', required=True)
@click.option('--fieldname', '-f', 'fieldname', required=True)
def lexicon(corpus, fieldname):
    c = Corpus(corpus)

    lexicon = set()
    for reader in c.readers:
        with CylleneusSearcher(reader) as searcher:
            lexicon.update(list(searcher.lexicon(fieldname)))
    if lexicon:
        click.echo(f"[+] lexicon '{fieldname}' of '{corpus}': {len(lexicon)} items")
        click.echo_via_pager('\n'.join([i.decode('utf8') for i in sorted(lexicon)]))
    else:
        click.echo(f'[-] failed')


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
