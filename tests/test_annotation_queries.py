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

        queries = [
            ":VB.",
            ":NN.",
            ":ADJ.",
            ":ADV.",
            ":GEN.",
            ":ACC.PL.",
            ":PRS.SBJV.",
            ":3SG.",
            ":M.PL.",
            ":VB.PL.",
            ":VB.SBJV.",
            #'"cum :ABL."',  # adjacency
            # "<virtus>:SG.",
            # "<virtus>:PL.",
            # "<virtus>:ABL.",
            # "<virtus>:PL.ABL.",
            # "<habeo>:3PL.",
            #"<habeo>:SBJV.",
            ]

        c = Corpus(choice(['lasla', 'perseus']))
        e = Searcher(c)

        results = list(e.search(choice(queries), debug=False).results)
        assert results is not None
