#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `cylleneus` package."""


import unittest
from search import Searcher
from corpus import Corpus
from random import choice


class TestAnnotationQueries(unittest.TestCase):
    """Tests for `cylleneus` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_annotation_queries(self):
        """Test possible annotation queries."""

        queries = {
            'form': "'ius'",
            'annotation': ":ACC.PL.",
            'lemma': "<virtus>",
            'lemma with annotation': "<animus>:PL.ABL.",
            'gloss (en)': "[en?war]",
            'gloss (it)': "[it?guerra]",
            'gloss (es)': "[es?guerra]",
            'gloss (fr)': "[fr?guerre]",
            'gloss with annotation': "[en?courage]:GEN.SG.",
            'semfield': "{611}",
            'form + lemma': '"cum <virtus>"',
            'form + lemma with annotation': '"cum <virtus>:SG."',
            'form + annotation': "'milites' :VB.",
            'annotation + form': ":VB. 'milites'",
            'annotation + lemma': ":VB. <miles>",
            'lexical relation (lemma)': "</=bellum>",
            'semantic relation (gloss)': "[!=en?love]",
            'semantic relation (synset)': "[@=n#04478900]",
        }

        c = Corpus(choice(['lasla', 'perseus', 'latin_library']))
        e = Searcher(c)
        for k, v in queries.items():
            results = list(e.search(v, debug=False).results)
            hits = len(set([hit.docnum for hit, _, _ in results]))
            matches = len(results)
            assert hits and matches
