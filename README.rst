=========
Cylleneus
=========

.. image:: https://img.shields.io/badge/cylleneus-next--gen%20search%20for%20electronic%20corpora%20of%20Greek%20and%20Latin-blue.svg
        :target: https://github.com/wmshort/cylleneus

.. image:: https://img.shields.io/pypi/v/cylleneus.svg
        :target: https://pypi.python.org/pypi/cylleneus

.. image:: https://img.shields.io/travis/wmshort/cylleneus.svg
        :target: https://travis-ci.org/wmshort/cylleneus

.. image:: https://readthedocs.org/projects/cylleneus/badge/?version=latest
        :target: https://cylleneus.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


* Free software: Apache Software License 2.0
* Documentation: https://cylleneus.readthedocs.io.


Overview
--------

Cylleneus is a next-generation search engine for electronic corpora of Latin (and eventually Greek), which enables texts to be searched on the basis of their semantic and morpho-syntactic properties. This means that, for the first time, texts can be searched by the *meanings* of words as well as by the kinds of grammatical constructions they occur in. Semantic search takes advantage of the `Latin WordNet 2.0 <https://latinwordnet.exeter.ac.uk/>`_ and is fully implemented, and thus is available for any annotated or plain-text corpus. Syntactic search functionality is still under development and is available for only certain structured corpora.


Features
--------

* Semantic search: find words based on their meanings in English, Italian, Spanish, or French
* Syntactic search: finds words based on the kinds of grammatical constructions they appear in
* Fast: once a corpus is indexed, searches are nearly instantaneous
* Sophisticated: query types can be combined into complex search patterns
* Extensible: indexing pipelines can be created for nearly any corpus type
* Free: completely open-source and redistributable


Installation
------------

Clone this repository, navigate to the appropriate directory, and run the following command from your command line:

``python setup.py install``

To setup a development environment, instead use:

``pip install -r requirements_dev.txt``


Setup
-----

The Cylleneus engine requires texts to be indexed before they can be searched. For convenience and testing, this repository comes configured with two pre-indexed mini-corpora: the texts of Caesar from the LASLA corpus, and the texts of Vergil from the Perseus Digital Library as made available in JSON format by the Classical Language Tool Kit. Ready-made scripts are provided for indexing texts from the Perseus Digital Library (in JSON or TEI XML format), the LASLA corpus, the PHI5 corpus, and from plain-text sources (for instance, the Latin Library). To index a corpus (or part of one), the raw source should be placed in an appropriately named directory within ``/corpus/text/<name>``. Then you can use any of the ready-made scripts in the ``scripts`` directory, modifying it for your own needs. The script for indexing texts from the Latin Library should be suitable for any plain-text source document. If you want to use texts from another corpus entirely, you will need to create an indexing pipeline tailored to the structure of that corpus. See the documentation for instructions.

To enable gloss-based searches, Cylleneus relies on the MultiWordNet. To prepare the library for use, launch the Python REPL and enter the following commands.

>>> from multiwordnet.db import compile
>>> for language in ['common', 'english', 'latin', 'french', 'spanish', 'italian', 'hebrew']:
...     compile(language)

To test that everything is working properly, run the battery of query tests in ```tests/test_query_types.py``` over the packaged subcorpora.


Searching
---------

Two interfaces are provided for conducting searches. A handy (but not fully functional) command-line interface permits quick-and-dirty single-term queries:

``$ cylleneus --query "<virtus>" --corpus lasla``

NB. Click's argument parser interferes with Cyelleneus's query parsing, so all queries must be surrounded by double-quotes on the command line -- therefore making adjacency and proximity searches impossible using this tool.

Run ``shell.py`` for a more robust, but slightly more clunky search interface. It can accommodate the full range of query types.

Currently, Cylleneus enables the following query types:

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

:Form: <...>:...
:Example: <virtus>:GEN.SG.
:Description: filters results for only genitive singular forms
:Form: [...]:...
:Example: [en?attack]:VB.PL.
:Description: filters results for only plural verb forms
:Form: {...}:...
:Example: {Anatomy}:ACC.
:Description: filters results for only accusative forms

Lexical-relation queries
~~~~~~~~~~~~~~~~~~~~~~~~

:Form: <?=...>
:Example: </=virtus>
:Description: matches any word with the specified lexical relation to the given lemma

Semantic-relation queries
~~~~~~~~~~~~~~~~~~~~~~~~~

:Form: [?=...]
:Example: [@=en?courage]
:Description: matches any word with the specified semantic relation to the given gloss
:Example: [@=n#05595229]
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

=======      ================
Code         Description
=======      ================
``\=``       derives from (e.g., `<\=femina>` would match any lemma derived from *femina*, namely, *femineus*)
``/=``       relates to (the converse of *derives from*)
``+c=``      composed of (e.g., `<+c=cum>` would match any lemma composed by *cum*)
``-c=``      composes (e.g., `<-c=compono>` would match lexical elements that compose *compono*, namely, *cum* and *pono*).
``<=``       participle (verbs only)
=======      ================

Types of semantic relations
~~~~~~~~~~~~~~~~~~~~~~~~~~~

=======      ================
Code         Description
=======      ================
``!=``       antonym of
``@=``       hypernym of
``~=``       hyponym of
``|=``       nearest to
``*=``       entails
``#m=``      member of
``#p=``      part of
``#s=``      substance of
``+r=``      has role
``%m=``      has member
``%p=``      has part
``%s=``      has substance
``-r=``      is role of
``>=``       causes
``^=``       see also
``$=``       verb group
``==``       attribute
=======      ================

Query types can be combined into complex adjacency or proximity searches. An adjacency search specifies a particular ordering of the query terms (typically, but not necessarily, sequential); a proximity search simply finds contexts where all the query terms occur, regardless of order.
Adjacency searches must be enclosed with double quotes ("..."), optionally specifying a degree of 'slop', that is, the number of words that may intervene between matched terms, using '~' followed by the number of permissible intervening words.

Examples
~~~~~~~~

``"cui dono"``              matches the literal string 'cui dono'

``"si quid <habeo>"``       matches 'si' followed by 'quid' followed by any form of *habeo*

``"cum :ABL."``             matches 'cum' followed by any word in the ablative causes

``"in <ager>:PL."``         matches 'in' followed by any plural form of *ager*

``"<magnus> <animus>"~2``   matches any form of *magnus* followed by any form of *animus*, including if separated by a single word

``<honos> <virtus>``        matches any context including both any form of *honos* and any form of *virtus*


To Do
-----

In no particular order...

* functionality for incremental indexing and user-specifiable subcorpora
* CLI matching functionality of shell
* fix ordering of matches in results based on available metadata
* improve morphological annotation matching: at indexing, tokens should indicate _only_ a form's variance from the base (lemma's) morphology; for searching, 'bald' annotation queries need to generate tokens capturing all possible variations for a given part of speech (see ``morphology.from_leipzig``, ``analysis.filtering.AnnotationFilter``)
* fix CTS sourcing for multi-line results
* variable context-length specification
* disentangle annotation-based results filtering from results highlighting
* remove `content` field from any document schema not associated with a plain-text corpus. Corpora for which referencing metadata is available should not store the original text along with the index. In these cases, the text should be sourced from an external text repository using only the supplied URN and ``meta`` information: global sentence ID, local sentence ID (e.g., within a passage), and word position within the local reference context. Standardize ``meta`` as a series of tuples: (PHI5 author ID, PHI5 work ID, PHI5 meta string), (a, b, c), (x, y, z . . .), (...). Except for plain-text corpora, results should not include the ``hit`` object or ``content``! Corpus-specific referencing metadata (e.g., annotations for speaker turns, section subtitles) should be included as a variable-length tuple following the standard referencing information.
* /= returns results for the target lemma?
* use Scaife Viewer as search front-end
* Perseus CTS text alignment
* complete PROIEL indexing pipeline
* implement high-order syntactic search for treebank data
* sembanking: manually-curated semantic mark-up for Greek and Latin texts
* Greek!


Credits
-------

The Cylleneus search engine is the creation of William Michael Short. It is (currently) based on the open-source Whoosh search engine by Matt Chaput, and makes extensive use of the Classical Language Tool Kit. This project does not distribute original text sources for any corpus, particularly when they fall under licensing agreements. Data from the Latin WordNet 2.0 is sourced from https://latinwordnet.exeter.ac.uk/ through a publicly accessible API. If any soruce code has not been properly attributed, please inform the maintainers of this repository immediately and omissions wil be rectified.
