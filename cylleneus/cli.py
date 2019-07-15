# -*- coding: utf-8 -*-

"""Console script for Cylleneus."""
import sys
import click

from index import Indexer
from corpus import Corpus
from pathlib import Path
from cylleneus import cylleneus


@click.group()
def main():
    """Indexing commands for Cylleneus."""
    pass

@main.command()
def shell():
    cylleneus.repl.run()

@main.command()
@click.option('--corpus', '-c', 'corpus', required=True)
def index(corpus):
    click.echo(f"Index of {corpus}")
    indexer = Indexer(Corpus(corpus))
    for docnum, doc in indexer.docs:
        if not (doc['author'] and doc['title']):
            click.echo(f"[{docnum}] {doc['author']}, {doc['title']}")
        else:
            click.echo(f"[{docnum}] {doc['filename']}")

@main.command()
@click.option('--corpus', '-c', 'corpus', required=True)
def clear(corpus):
    click.echo(f"Clearing {corpus}... ", nl=False)
    indexer = Indexer(Corpus(corpus))
    indexer.clear()
    if indexer.index.doc_count_all() == 0:
        click.echo('ok')
    else:
        click.echo('failed')

@main.command()
@click.option('--corpus', '-c', 'corpus', required=True)
def create(corpus):
    click.echo(f"Creating {corpus}... ", nl=False)
    indexer = Indexer(Corpus(corpus))
    indexer.create()
    if indexer.index:
        click.echo('ok')
    else:
        click.echo('failed')

@main.command()
@click.option('--corpus', '-c', 'corpus', required=True)
def optimize(corpus):
    click.echo(f"Optimizing {corpus}...", nl=False)
    indexer = Indexer(Corpus(corpus))
    indexer.optimize()
    click.echo("ok")

@main.command()
@click.option('--corpus', '-c', 'corpus', required=True)
@click.option('--docnum', '-d', 'docnum', required=True)
def delete(corpus, docnum):
    indexer = Indexer(Corpus(corpus))
    indexer.delete(int(docnum))

@main.command()
@click.option('--corpus', '-c', 'corpus', required=True)
@click.option('--author', '-a', 'author')
@click.option('--title', '-t', 'title')
def deleteby(corpus, author, title):
    indexer = Indexer(Corpus(corpus))
    indexer.delete_by(author=author, title=title)


@main.command()
@click.option('--corpus', '-c', 'corpus', required=True)
@click.option('--author', '-a', 'author')
@click.option('--title', '-t', 'title')
def deleteby(corpus, author, title):
    indexer = Indexer(Corpus(corpus))
    indexer.delete_by(author=author, title=title)

@main.command()
@click.option('--corpus', '-c', 'corpus', required=True)
@click.option('--docnum', '-d', 'docnum', required=True)
@click.option('--path', '-p', 'path', required=True)
def update(corpus, docnum, file):
    indexer = Indexer(Corpus(corpus))
    indexer.update(docnum=docnum, path=Path(file))

@main.command()
@click.option('--corpus', '-c', 'corpus', required=True)
@click.option('--author', '-a', 'author')
@click.option('--title', '-t', 'title')
@click.option('--path', '-p', 'path', required=True)
def updateby(corpus, author, title, path):
    indexer = Indexer(Corpus(corpus))
    indexer.update_by(author=author, title=title, path=Path(path))

@main.command()
@click.option('--corpus', '-c', 'corpus', required=True)
@click.option('--path', '-p', 'path', required=True)
@click.option('--author', '-a', 'author')
@click.option('--title', '-t', 'title')
def add(corpus, path, author, title):
    click.echo(f"Adding {path}... ", nl=False)
    indexer = Indexer(Corpus(corpus))
    n = indexer.index.doc_count_all()
    indexer.add(Path(path), author, title)
    if indexer.index.doc_count_all() > n:
        click.echo("ok")
    else:
        click.echo("failed")

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
