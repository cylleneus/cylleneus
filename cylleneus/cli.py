# -*- coding: utf-8 -*-

"""Console script for Cylleneus."""

import sys
from pathlib import Path

import click
import click_spinner

from cylleneus.corpus import Corpus, Work, manifest
from cylleneus.search import CylleneusSearcher
from cylleneus.settings import CORPUS_DIR
from cylleneus.utils import slugify
import cylleneus.engine
from cylleneus import __version__

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
def version():
    """Display the current engine version number. """

    click.echo(f"[+] Cylleneus v{__version__}")


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
@click.option("--verbose", "-v", is_flag=True)
@click.option("--dry-run", "-d", is_flag=True)
def verify(corpus, verbose, dry_run):
    """Verify the integrity of corpus indexes and manifest. """

    c = Corpus(corpus)
    manifest = c.manifest
    if c.index_dir.exists() and click.confirm(
        f"{len(manifest)} documents manifested for corpus '{c.name}'. "
        + (f"This might take a while! " if len(manifest) > 30 else "")
        + f"Proceed?",
        default=True,
    ):
        verified = []
        passes = fixes = adds = orphans = 0
        missing = {}

        with click.progressbar(
            manifest,
            length=len(manifest),
            show_percent=True,
            label=f"Verifying '{c.name}'",
        ) as bar:
            for item in bar:
                status, (docix, author, title, filename, info) = c.verify_by_docix(
                    item, dry_run=dry_run
                )
                msg = f"[{docix}] {author}, {title} ({filename})"
                if status == 0:
                    msg += ", passed!"
                    passes += 1
                elif status == 1:
                    msg += ", fixed in manifest"
                    fixes += 1
                elif status == 2:
                    msg += ", added to manifest"
                    adds += 1
                elif status == 3:
                    msg += ", deleted orphaned index files"
                    orphans += 1
                elif status == 4:
                    msg = f"[{docix}] {manifest[item]['author']}, {manifest[item]['title']} (" \
                          f"{manifest[item]['filename']})"
                    msg += ", missing index files!"
                    missing[item] = manifest[item]
                if info is not None and cylleneus.settings.DEBUG:
                    msg += f" (= {info})"
                verified.append((docix, msg))
        if verbose and len(verified) != 0:
            click.echo_via_pager(
                "\n".join(
                    [
                        ("*" if dry_run else "") + item[1]
                        for item in sorted(verified, key=lambda item: item[0])
                    ]
                )
            )
        click.echo(
            f"[-] '{corpus}': {len(manifest)} checked, {passes} passed"
            + (f", {fixes} fixed in manifest" if fixes else "")
            + (f", {adds} added to manifest, " if adds else "")
            + (f", {orphans} orphaned files deleted" if orphans else "")
            + (
                f" -- changes have NOT been committed!"
                if dry_run and passes < len(manifest)
                else ""
            )
        )
        if len(missing) != 0:
            if click.confirm(
                f"Try to re-index {len(missing)} missing documents?", default=True,
            ):
                for docix, meta in missing.items():
                    if meta["filename"]:
                        path = c.text_dir / Path(meta["filename"])
                        with click_spinner.spinner():
                            updated_docix = (
                                c.update(docix, path) if not dry_run else None
                            )
                        if updated_docix is not None:
                            click.echo(
                                f"[{updated_docix}] {meta['author']}, {meta['title']} ({meta['filename']}), "
                                f"index created!"
                            )
                        else:
                            if dry_run:
                                click.echo(
                                    f"*[-] {meta['author']}, {meta['title']} "
                                    f"({meta['filename']}) -- document NOT re-indexed!"
                                )
                            else:
                                click.echo(
                                    f"[-] {meta['author']}, {meta['title']} ({meta['filename']}), failed"
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

        if c.searchable:
            click.echo("[-] failed")
        else:
            click.echo(f"[+] destroyed '{corpus}'")


@main.command()
@click.option("--corpus", "-c", "corpus", required=True)
def optimize(corpus):
    """Optimize the indexes of a corpus. """

    with click_spinner.spinner():
        c = Corpus(corpus)
        if c.searchable:
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
def delete_by(corpus, **kwargs):
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

    docix = int(docix)
    with click_spinner.spinner():
        c = Corpus(corpus)
        c.update(docix=docix, path=Path(path))

    if c.work_by_docix(docix).searchable:
        click.echo(f"[+] updated document {docix} in '{corpus}'")
    else:
        click.echo(f"[-] failed")


@main.command()
@click.option("--corpus", "-c", "corpus", required=True)
@click.option("--author", "-a", "author")
@click.option("--title", "-t", "title")
@click.option("--path", "-p", "path", required=True)
def update_by(corpus, **kwargs):
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
            c = Corpus(corpus)
            try:
                c.download(branch)
            except Exception as e:
                click.echo("[-] failed", e)


@main.command()
@click.option("--corpus", "-c", "corpus", required=True)
@click.option("--docix", "-i", "docix", required=False)
def download_by_docix(corpus, docix):
    """Download a document by number from a remote corpus. """

    if corpus not in REMOTE_CORPORA:
        click.echo(f"[-] no remote location for '{corpus}'")
    else:
        c = Corpus(corpus)
        try:
            if not docix:
                manifest = c.remote_manifest()
                for docix, meta in manifest.items():
                    click.echo(
                        f"[{docix}] {meta['author']}, {meta['title']} [{meta['filename']}]"
                    )
            else:
                with click_spinner.spinner():
                    c.download_by_docix(int(docix))
                meta = c.manifest[docix]
                click.echo(
                    f"[{docix}] {meta['author']}, {meta['title']} [{meta['filename']}]"
                )
        except Exception as e:
            click.echo("[-] failed", e)


@main.command()
@click.option("--corpus", "-c", "corpus", required=True)
@click.option("--author", "-a", "author", required=False)
@click.option("--title", "-t", "title", required=False)
def download_by(corpus, author, title):
    """Download documents by author and title from a remote corpus. """

    if corpus not in REMOTE_CORPORA:
        click.echo(f"[-] no remote location for '{corpus}'")
    else:
        try:
            c = Corpus(corpus)
            if not author and not title:
                manifest = c.remote_manifest()
                for docix, meta in manifest.items():
                    click.echo(
                        f"[{docix}] {meta['author']}, {meta['title']} [{meta['filename']}]"
                    )
            else:
                n = len(c.manifest)
                with click_spinner.spinner():
                    c.download_by(author, title)
                click.echo(f"[+] downloaded {len(c.manifest) - n} documents")
        except Exception as e:
            click.echo("[-] failed", e)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
