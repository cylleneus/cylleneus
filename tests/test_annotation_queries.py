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
            'verb': ":VB.",
            'noun': ":NN.",
            'adjective': ":ADJ.",
            'adverb': ":ADV.",
            'genitive': ":GEN.",
            'accusative plural': ":ACC.PL.",
            'present subjunctive': ":PRS.SBJV.",
            '2nd person singular': ":2SG.",
            'masculine plural': ":M.PL.",
            'virtus, singular': "<virtus>:SG.",
            'virtus, plural': "<virtus>:PL.",
            'virtus, ablative': "<virtus>:ABL.",
            'virtus, ablative plural': "<virtus>:PL.ABL.",
            'habeo, 3rd person plural': "<habeo>:3PL.",
            'verb, plural': ":VB.PL.",
            'habeo, subjunctive': "<habeo>:SBJV.",
            'verb, subjunctive plural': ":VB.PL.SBJV.",
            'cum + ablative': '"cum :ABL."',  # adjacency
            }

        c = Corpus(choice(['lasla', 'perseus']))
        e = Searcher(c)
        for k, v in queries.items():
            results = list(e.search(v, debug=False).results)
            hits = len(set([hit.docnum for hit, _, _ in results]))
            matches = len(results)
            assert hits and matches
