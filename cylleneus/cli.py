# -*- coding: utf-8 -*-

"""Console script for Cylleneus."""

import sys
from pathlib import Path

import click
import click_spinner

from cylleneus.corpus import Corpus, Work, manifest
from cylleneus.search import CylleneusSearcher
from cylleneus.settings import CORPUS_DIR

REMOTE_CORPORA = {
    name: meta for name, meta in manifest.items() if meta.repo["location"] == "remote"
}


@click.group()
def main():
    """Indexing commands for Cylleneus."""


@main.command()
def where():
    """Display location of corpus directory. """

    click.echo(f"[-] {CORPUS_DIR}")


@main.command()
@click.option("--corpus", "-c", "corpus", required=True)
def index(corpus):
    """List indexed works in a corpus. """

    c = Corpus(corpus)
    docs = sorted(c.iter_docs(), key=lambda x: x[0])

    if docs:
        for docix, doc in docs:
            if "author" in doc and "title" in doc:
                click.echo(
                    f"[{doc['docix']}] {doc['author']}, {doc['title']} [{doc['filename']}]"
                )
            else:
                click.echo(f"[{doc['docix']}] {doc['filename']}")
    else:
        click.echo(f"[-] nothing indexed for '{corpus}'")


@main.command()
@click.option("--corpus", "-c", "corpus", required=True)
def verify(corpus):
    """Verify the indexes of a corpus against its manifest. """

    c = Corpus(corpus)
    docs = sorted(c.iter_docs(), key=lambda x: x[0])
    manifest = c.manifest

    for docix, doc in docs:
        docix = str(docix)
        try:
            matched = all(
                manifest[docix][k] == doc[k] for k in ["author", "title", "filename"]
            )
        except KeyError:
            click.echo(
                f"[{doc['docix']}] {doc['author']}, {doc['title']} ({doc['filename']})]... not "
                f"in manifest!"
            )
        else:
            click.echo(
                f"[{doc['docix']}] {doc['author']}, {doc['title']} ({doc['filename']})... "
                f"{'manifest ✓' if matched else 'manifest ✗'}, "
                f"{'index ✓' if c.work_by_docix(int(docix)).is_searchable else 'index ✗'}"
            )


@main.command()
@click.option("--corpus", "-c", "corpus", required=True)
def clear(corpus):
    """Clear the indexes of a corpus without deleting them. """

    with click_spinner.spinner():
        c = Corpus(corpus)
        c.clear()

    if c.doc_count_all == 0:
        click.echo(f"[+] cleared '{corpus}'")
    else:
        click.echo("[-] failed")


@main.command()
@click.option("--corpus", "-c", "corpus", required=True)
def destroy(corpus):
    """Destroy the indexes and manifest of a corpus. """

    if click.confirm(f"Are you sure?", default=False):
        with click_spinner.spinner():
            c = Corpus(corpus)
            c.destroy()

        if c.is_searchable:
            click.echo("[-] failed")
        else:
            click.echo(f"[+] destroyed '{corpus}'")


@main.command()
@click.option("--corpus", "-c", "corpus", required=True)
def optimize(corpus):
    """Optimize the indexes of a corpus. """

    with click_spinner.spinner():
        c = Corpus(corpus)
        if c.is_searchable:
            c.optimize()
            click.echo(f"[+] optimized '{corpus}'")
        else:
            click.echo(f"[-] failed")


@main.command()
@click.option("--corpus", "-c", "corpus", required=True)
@click.option("--docix", "-d", "docix", required=True)
def delete(corpus, docix):
    """Delete a document in a corpus by index number. """

    with click_spinner.spinner():
        c = Corpus(corpus)
        c.delete_by_ix(int(docix))

    if docix in list(c.all_doc_ixs()):
        click.echo(f"[-] failed")
    else:
        click.echo(f"[+] deleted document {docix} of '{corpus}'")


@main.command()
@click.option("--corpus", "-c", "corpus", required=True)
@click.option("--author", "-a", "author")
@click.option("--title", "-t", "title")
def deleteby(corpus, **kwargs):
    """Delete documents in a corpus by author name and/or title. """

    with click_spinner.spinner():
        c = Corpus(corpus)
        pre_ndocs = c.doc_count_all
        c.delete_by()
        post_ndocs = c.doc_count_all
        ndocs = pre_ndocs - post_ndocs

    if ndocs == 0:
        click.echo(f"[-] failed")
    else:
        click.echo(f"[+] deleted {ndocs} documents from '{corpus}'")


@main.command()
@click.option("--corpus", "-c", "corpus", required=True)
@click.option("--docix", "-d", "docix", required=True)
@click.option("--path", "-p", "path", required=True)
def update(corpus, docix, path):
    """Reindex a document by index number. """

    with click_spinner.spinner():
        c = Corpus(corpus)
        c.update(docix=docix, path=Path(path))

    if docix in [doc["docix"] for doc in c.iter_docs()]:
        click.echo(f"[+] updated document {docix} in '{corpus}'")
    else:
        click.echo(f"[-] failed")


@main.command()
@click.option("--corpus", "-c", "corpus", required=True)
@click.option("--author", "-a", "author")
@click.option("--title", "-t", "title")
@click.option("--path", "-p", "path", required=True)
def updateby(corpus, **kwargs):
    """Reindex a document by author name and/or title. """

    with click_spinner.spinner():
        kwargs["path"] = Path(kwargs["path"])
        c = Corpus(corpus)
        docix = c.update_by(**kwargs)

    if docix in [doc["docix"] for doc in c.iter_docs()]:
        click.echo(f"[+] updated document {docix} in '{corpus}'")
    else:
        click.echo(f"[-] failed")


@main.command()
@click.option("--corpus", "-c", "corpus", required=True)
@click.option("--path", "-p", "path", required=True)
@click.option("--author", "-a", "author")
@click.option("--title", "-t", "title")
def add(corpus, path, author, title):
    """Index a specific file. """

    with click_spinner.spinner():
        c = Corpus(corpus)
        pre_ndocs = c.doc_count_all

        w = Work(c, author, title)
        _ = w.indexer.from_file(Path(path))

    post_ndocs = c.doc_count_all
    ndocs = post_ndocs - pre_ndocs
    if post_ndocs > pre_ndocs:
        click.echo(
            f"[+] added {ndocs} document{'s' if ndocs > 1 else ''} to '{corpus}'"
        )
    else:
        click.echo("[-] failed")


@main.command()
@click.option("--corpus", "-c", "corpus", required=True)
@click.option("--destructive/--not-destructive", "-d/-D", default=True)
@click.option("--optimize", "-o", is_flag=True)
def create(corpus, destructive, optimize):
    """Create all corpus indexes from source files. """

    with click_spinner.spinner():
        c = Corpus(corpus)
        if destructive:
            c.destroy()
        for file in c.text_dir.glob(c.glob):
            w = Work(corpus=c)
            _ = w.indexer.from_file(file, destructive=destructive, optimize=optimize)

    ndocs = c.doc_count_all
    if ndocs > 0:
        click.echo(
            f"[+] created '{corpus}' with {ndocs} document{'s' if ndocs > 1 else ''}"
        )
    else:
        click.echo("[-] failed")


@main.command()
@click.option("--corpus", "-c", "corpus", required=True)
@click.option("--fieldname", "-f", "fieldname", required=True)
def lexicon(corpus, fieldname):
    """List the contents of an index by field name. """

    c = Corpus(corpus)

    lexicon = set()
    for reader in c.readers:
        with CylleneusSearcher(reader) as searcher:
            lexicon.update(list(searcher.lexicon(fieldname)))
    if lexicon:
        click.echo(f"[+] lexicon '{fieldname}' of '{corpus}': {len(lexicon)} items")
        click.echo_via_pager("\n".join([i.decode("utf8") for i in sorted(lexicon)]))
    else:
        click.echo(f"[-] failed")


@main.command()
@click.option("--corpus", "-c", "corpus", required=False)
@click.option("--branch", "-b", "branch", required=False)
def download(corpus, branch):
    """Download a remote corpus repository. """

    if not corpus:
        for name, meta in REMOTE_CORPORA.items():
            click.echo(f"[-] '{name}' [{meta.repo['origin']}]")
    else:
        if corpus not in REMOTE_CORPORA:
            click.echo(f"[-] no remote location for '{corpus}'")
        else:
            if click.confirm(
                f"This will overwrite any index files! Are you sure?", default=False
            ):
                c = Corpus(corpus)
                try:
                    c.download(branch)
                except Exception as e:
                    click.echo("[-] failed", e)
            else:
                click.echo("[-] aborted")


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
