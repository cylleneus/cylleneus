# -*- coding: utf-8 -*-

"""Console script for Cylleneus."""
import sys
import click

from index import Indexer
from corpus import Corpus
from pathlib import Path

@click.group()
def main():
    """Indexing commands for Cylleneus."""
    pass

@main.command()
@click.option('--corpus', '-c', 'corpus', required=True)
def index(corpus):
    indexer = Indexer(Corpus(corpus))
    for docnum, doc in indexer.docs:
        click.echo(f"[{docnum}] {doc['author']}, {doc['title']}")

@main.command()
@click.option('--corpus', '-c', 'corpus', required=True)
def clear(corpus):
    indexer = Indexer(Corpus(corpus))
    indexer.clear()

@main.command()
@click.option('--corpus', '-c', 'corpus', required=True)
def create(corpus):
    indexer = Indexer(Corpus(corpus))
    indexer.create()

@main.command()
@click.option('--corpus', '-c', 'corpus', required=True)
def optimize(corpus):
    indexer = Indexer(Corpus(corpus))
    indexer.optimize()

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
    indexer = Indexer(Corpus(corpus))
    indexer.add(Path(path), author, title)

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
