=========
Cylleneus
=========

.. image:: https://img.shields.io/badge/cylleneus-next--gen%20corpus%20search%20for%20electronic%20corpora%20of%20ancient%20languages-blue
        :target: https://github.com/cylleneus/cylleneus

.. image:: https://img.shields.io/pypi/v/cylleneus.svg
        :target: https://pypi.python.org/pypi/cylleneus

.. image:: https://travis-ci.org/cylleneus/cylleneus.svg?branch=master
    :target: https://travis-ci.org/cylleneus/cylleneus

.. image:: https://readthedocs.org/projects/cylleneus/badge/?version=latest
        :target: https://cylleneus.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status
        
.. image:: https://mybinder.org/badge_logo.svg
        :target: https://mybinder.org/v2/gh/cylleneus/cylleneus/master?filepath=quick_search.ipynb


* Free software: Apache Software License 2.0
* Documentation: https://cylleneus.readthedocs.io.


Overview
--------

Cylleneus is a next-generation search engine for electronic corpora of Greek and Latin, which enables texts to be searched on the basis of their semantic and morpho-syntactic properties. This means that, for the first time, texts can be searched by the *meanings* of words as well as by the kinds of grammatical constructions they occur in. Semantic search takes advantage of the `Ancient Greek WordNet <https://greekwordnet.chs.harvard.edu/>`_, `Latin WordNet <https://latinwordnet.exeter.ac.uk/>`_ and `Sanskrit WordNet <http://sanskritwordnet.unipv.it/>`_ and is fully implemented, and thus is available for any annotated or plain-text corpus. However, semantic queries may still be imprecise due to the on-going nature of these two projects. Syntactic search functionality is still under development and is available for only certain structured corpora.  Morphological searching and query filtering will work with any Latin corpus, and any Greek corpus with sufficient morhological annotation.


Features
--------

* Advanced search capabilities for Greek, Latin, Sanskrit (and soon ancient Egyptian)
* Semantic search: find words based on their meanings in English, Italian, Spanish, or French
* Syntactic search: finds words based on the kinds of grammatical constructions they appear in
* Morphological search: find words, or filter the results of other queries, based on morphological properties
* Fast: once a corpus is indexed, most query types produce results nearly instantaneously
* Sophisticated: query types can be combined into complex search patterns
* Extensible: indexing pipelines can be created for any corpus type 
* Currently supports: Atlas, AGLDT, LASLA, Perseus (XML or JSON format), CAMENA, PROIEL and any plaintext source (e.g. Digital Latin Library); Digital Corpus of Sanskrit; Ramses. Diorisis support in development.
* Free: completely open-source and redistributable


Installation
------------

``pip install cylleneus``


Setup
-----

The Cylleneus engine requires texts to be indexed before they can be searched. For convenience and testing, several pre-indexed mini-corpora are available. These need to be placed in a proper folder hierarchy within the user's data directory.

MacOS
``~/Library/Application Support/Cylleneus/corpus``

Windows
``C:\Documents and Settings\<User>\Application Data\Local Settings\Cylleneus\corpus`` or
``C:\Documents and Settings\<User>\AppData\Local\Cylleneus\corpus``

Linux:
``~/.local/share/Cylleneus/corpus``

To enable gloss-based searches, Cylleneus relies on the MultiWordNet. The setup process should install the latest version of the ``multiwordnet`` library, and also compile the necessary databases, but in case this step has been omitted you can do it manually. To do so, launch the Python REPL and enter the following commands.

>>> from multiwordnet.db import compile
>>> for language in ['common', 'english', 'latin', 'french', 'spanish', 'italian', 'hebrew']:
...     compile(language)

To test that everything is working properly, run the battery of query tests in ``tests/test_query_types.py`` over the packaged subcorpora.


Indexing
--------

Ready-made tools are provided for indexing texts from the Perseus Digital Library (in JSON or TEI XML format), the LASLA corpus, the PROIEL corpus, the AGLDT corpus, the PHI5 corpus, and from plain-text sources (for instance, the Latin Library). To index a corpus (or part of one), the raw source should be placed in an appropriately named directory within ``/corpus/<name>/text/``. Then you can use any of the scripts in the ``scripts`` directory, modifying it for your own needs. The script for indexing texts from the DLL can be adapted to any plain-text source document. If you want to use texts from another corpus entirely, you will need to create an indexing pipeline tailored to the structure of that corpus. See the documentation for instructions.

Basic indexing functionality is also provided through a command-line interface. ``$ cylleneus --help`` displays the complete list of available indexing commands.

To create the index for a corpus, you will need to have a folder ``text`` in an appropriately named directory. (For examples of the correct directory structure, see the sample corpora).

``$ cylleneus create --corpus latin_library  # create the 'latin_library' corpus from scratch using the available texts``

To add a document or documents to a corpus, you must provide the original source files and indicate the correct path.

``$ cylleneus index --corpus perseus  # display the current index of corpus 'perseus'``

``$ cylleneus add --corpus lasla --path "/corpus/lasla/texts/Catullus_Catullus_Catul.BPN"  # for plaintext corpora you will also need to specify --author and --title, as this cannot be inferred from filenames or other metadata``

Indexes should probably always be optimized, though this process can be slow if the corpus is large.

``$ cylleneus optimize --corpus latin_library``


Searching
---------

The best way to search the available corpora (or to import new files individually) is to use the web app or shell script, available separately. Searches can of course also be conducted programmatically via the library's API.

``>>> from cylleneus.corpus import Corpus``

``>>> from cylleneus.search import Searcher, Collection``

``>>> corpus = Corpus("perseus")``

``>>> clct = Collection(corpus.works)``

``>>> searcher = Searcher(clct)``

``>>> results = searcher.search("<habeo>")``


Query Types
-----------

Currently, Cylleneus enables the following types of queries:

Word-form queries
~~~~~~~~~~~~~~~~~

:Form: '...'
:Example: 'virtutem'
:Description: matches a literal string

Lemma-based queries
~~~~~~~~~~~~~~~~~~~

:Form: <...>
:Example: <virtus>
:Description: matches any form of the specified lemma

More precision can be introduced by using LEMLAT URIs, along with morphological tagging. For example, in the Cylleneus shell ``search <dico>`` will match occurrences both of *dico*, *dicere* and of *dico*, *dicare*. To distinguish between them, you can use the relevant URIs: ``<dico:d1349>`` (*dicare*) or ``<dico:d1350>``. Alternatively, you can specify an appropriate morphological tag: ``<dico=v1spia--3->`` or <dico=v1spia--1->``.

Gloss-based queries
~~~~~~~~~~~~~~~~~~~

:Form: [...]
:Example: [en?courage]
:Description: matches any word with the same meaning as the specified gloss. Can be 'en', 'it', 'es', or 'fr'.
:Example: [n#05595229]
:Description: matches any word with the meaning defined by the specified synset offset ID

Domain-based queries
~~~~~~~~~~~~~~~~~~~~

:Form: {...}
:Example: {611}, {Anatomy}
:Description: matches any word of any part of speech whose meaning falls within the specified domain. Cylleneus uses the Dewey Decimal Classification System as a general topic index.

Morphology-based queries
~~~~~~~~~~~~~~~~~~~~~~~~

:Form: :...
:Example: :ACC.SG.
:Description: matches any word with the specified morphological properties, given in Leipzig notation. Annotations can be given as distinct query terms, or can be used as filters for lemma- or gloss-based queries. (For example, ``<virtus>:PL.`` will match only plural forms of this word).

Morphology-based filtering
~~~~~~~~~~~~~~~~~~~~~~~~~~

:Form: <...>|...
:Example: <virtus>|GEN.SG.
:Description: filters results for only genitive singular forms
:Form: [...]:...
:Example: [en?attack]¦VB.PL.
:Description: filters results for only plural verb forms
:Form: {...}:...
:Example: {Anatomy}|ACC.
:Description: filters results for only accusative forms

Lexical-relation queries
~~~~~~~~~~~~~~~~~~~~~~~~

:Form: <?::...>
:Example: </::virtus>
:Description: matches any word with the specified lexical relation to the given lemma

Semantic-relation queries
~~~~~~~~~~~~~~~~~~~~~~~~~

:Form: [?::...]
:Example: [@::en?courage]
:Description: matches any word with the specified semantic relation to the given gloss
:Example: [@::n#05595229]
:Description: matches any word with the specified semantic relation to the given synset

Syntax-based queries
~~~~~~~~~~~~~~~~~~~~

:Form: /.../
:Example: /ablative absolute/
:Description: syntactical constructions (currently, only the LASLA corpus supports this)

Gloss-based searches enable searching by the meanings of words, and queries can be specified in English (en?), Italian (it?), Spanish (es?), or French (fr?). (NB. The vocabulary for Italian, Spanish, and French is significantly smaller than English).
It is also possible to search by synset ID number: this capability is exposed for future development of an interface where users can search for a specific sense. Normally, queries will be specified as English terms, which resolve to sets of synsets.
Queries involving lexical and semantic relations depend on information available from the Latin Wordnet 2.0. As this project is on-going, rich relational information may be available only for a subset of vocabulary. However, as new information becomes available, search results should become more comprehensive and more accurate.

Types of lexical relations
~~~~~~~~~~~~~~~~~~~~~~~~~~

=======        ================
Code           Description
=======        ================
``\``          derives from (e.g., ``<\::femina>`` would match any lemma derived from *femina*, namely, *femineus*)
``/``          relates to (the converse of *derives from*)
``+c``         composed of (e.g., ``<+c::cum>`` would match any lemma composed by *cum*)
``-c``         composes (e.g., ``<-c::compono>`` would match lexical elements that compose *compono*, namely, *cum* and *pono*).
``<``          participle (verbs only)
=======        ================

Types of semantic relations
~~~~~~~~~~~~~~~~~~~~~~~~~~~

=======     ================
Code        Description
=======     ================
``!``       antonym of
``@``       hypernym of
``~``       hyponym of
``|``       nearest to
``*``       entails
``#m``      member of
``#p``      part of
``#s``      substance of
``+r``      has role
``%m``      has member
``%p``      has part
``%s``      has substance
``-r``      is role of
``>``       causes
``^``       see also
``$``       verb group
``=``       attribute
=======     ================

Query types can be combined into complex adjacency or proximity searches. An adjacency search specifies a particular ordering of the query terms (typically, but not necessarily, sequential); a proximity search simply finds contexts where all the query terms occur, regardless of order.
Adjacency searches must be enclosed with double quotes ("..."), optionally specifying a degree of 'slop', that is, the number of words that may intervene between matched terms, using '~' followed by the number of permissible intervening words.

Examples
~~~~~~~~

``"cui dono"``              matches the literal string 'cui dono'

``"si quid <habeo>"``       matches 'si' followed by 'quid' followed by any form of *habeo*

``"cum :ABL."``             matches 'cum' followed by any word in the ablative causes

``"in <ager>|PL."``         matches 'in' followed by any plural form of *ager*

``"<magnus> <animus>"~2``   matches any form of *magnus* followed by any form of *animus*, including if separated by a single word

``<honos> <virtus>``        matches any context including both any form of *honos* and any form of *virtus*


To Do
-----

In no particular order...

* Optimization
* Perseus CTS alignment for corpora with non-standard text annotations
* implement high-order syntactic search for different annotation schemes
* manually-curated WordNet-based semantic mark-up ('sembanks') for texts


Credits
-------

© 2019 William Michael Short. Based on the open-source Whoosh search engine by Matt Chaput.
