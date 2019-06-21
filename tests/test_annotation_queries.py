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

        from multiwordnet.db import compile
        for language in ['common', 'latin', 'italian', 'spanish', 'french', 'hebrew']:
            compile(language)

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
            '3rd person singular': ":3SG.",
            'masculine plural': ":M.PL.",
            'verb, plural': ":VB.PL.",
            'verb, subjunctive': ":VB.SBJV.",
            'cum + ablative': '"cum :ABL."',  # adjacency
            # 'virtus, singular': "<virtus>:SG.",
            # 'virtus, plural': "<virtus>:PL.",
            # 'virtus, ablative': "<virtus>:ABL.",
            # 'virtus, ablative plural': "<virtus>:PL.ABL.",
            # 'habeo, 3rd person plural': "<habeo>:3PL.",
            # 'habeo, subjunctive': "<habeo>:SBJV.",
            }

        c = Corpus(choice(['lasla', 'perseus']))
        e = Searcher(c)

        for k, v in queries.items():
            results = list(e.search(v, debug=False).results)
            assert results
