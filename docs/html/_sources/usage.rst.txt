=====
Usage
=====

To use Cylleneus in a project::

    import cylleneus


To use Cylleneus with a different corpus, for which indexing infrastructure does not already exist, three things will be required::

1. A unique document Schema (see ``engine.schemas`` for examples), which specifies the available fields for searching. At minimum, every schema should include the following fields: ``author`` (the name of the author)
    ``title`` (the name of the work)
    ``urn`` (a Perseus CTS URN, if available, for remote text sourcing)
    ``meta`` (a dash-separated lowercase string giving the labels of the work's divisions, e.g.: 'book-section-line', if available)
    ``form`` (for literal word-form queries)
    ``lemma`` (for lemma-based queries)
    ``annotation`` (for morphological queries)
    ``synset`` (for gloss-based queries)
    ``semfield`` (for domain-based queries)
Plain-text document schemas must also include a ``content`` field for storing the original text along with the index. This is because plain-text corpora do not include reliable referencing metadata and so cannot be used with external text hosting services.
Additional fields can be included if the corpus provides extra information. For instance, the schema for documents from the LASLA corpus has an additional field ``morphosyntax`` which is used for indexing the syntactic codes provided by this annotated corpus.

2. A specialized Tokenizer (see ``engine.analysis.tokenizers`` for examples) for transforming a raw source document into a stream of word tokens.

3. Any specialized Filters (see ``engine.analysis.filters`` for examples) for extracting information from the raw source document.
