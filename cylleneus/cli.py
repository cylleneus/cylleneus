# -*- coding: utf-8 -*-

"""Console script for Cylleneus."""
import sys
import click

from search import Searcher
from corpus import Corpus


QUERY_TYPES = """
Queries can be any of the following possible forms:
    'virtutem'          form
    <virtus>            lemma
    [en?courage]        gloss
    {Anatomy}           domain
    :ACC.SG.            morphology
    </=virtus>          lexical relation
    [@=n#05595229]      semantic relations
    /ablative absolute/ syntactic constructions
"""


@click.command()
@click.option('--query', '-q', 'query')
@click.option('--corpus', '-c', 'corpus', required=True)
@click.option('--list', '-l', 'list', is_flag=True)
def main(query, corpus, list):
    """Console script for Cylleneus."""

    if list:
        s = '\n'.join([f"{docnum}. {fields['author'].title()}, {fields['title'].title()}"
                       for docnum, fields in Corpus(corpus).index.reader().iter_docs()])
        click.echo(s)
    else:
        if query:
            searcher = Searcher(Corpus(corpus))

            # TODO: fix query parsing
            search = searcher.search(query)
            click.echo_via_pager(search.highlights)
        else:
            click.echo(QUERY_TYPES)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
