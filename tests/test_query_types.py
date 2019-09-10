#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `cylleneus` package."""


import unittest
from random import choice

from corpus import Corpus
from search import Searcher, Collection


class TestQueryTypes(unittest.TestCase):
    """Tests for `cylleneus` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

        from multiwordnet.db import compile
        for language in ['common', 'latin', 'italian', 'spanish', 'french', 'hebrew']:
            compile(language)

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_query_types(self):
        """Test permissible query types."""

        queries = [
            ("lasla", "'sed'", (235, 2, 1)),
            ("lasla", ":ACC.PL.", (3152, 2, 1)),
            ("latin_library", "<habeo>", (139, 6, 1)),
            ("lasla", "<animus>|ABL.SG.", (33, 2, 1)),
            ("perseus", "[en?war]", (208, 3, 1)),
            ("lasla", "[it?guerra]", (308, 2, 1)),
            ("lasla", "[en?courage]|ABL.PL.", (10, 2, 1)),
            ("latin_library", "{611}", (2042, 6, 1)),
            ("perseus", '"cum clamore"', (2, 2, 1)),
            ("perseus", '"cum <clamor>"', (3, 2, 1)),
            ("perseus", '"cum <clamor>|ABL."', (2, 2, 1)),
            ("perseus", '"cum magno" <calor>', (1, 1, 1)),
            # ("perseus", '"deceptus <amor>|ABL.SG."', (1, 1, 1)),
            ("lasla", '":VB. milites"', (8, 2, 1)),
            ("lasla", '":VB. <miles>"', (10, 2, 1)),
            ("perseus", "</::bellum>", (127, 3, 1)),
            ("lasla", "[!::en?cowardice]", (272, 2, 1)),
            ("latin_library", "[@::n#04478900]", (20, 6, 1)),
        ]
        c, q, n = choice(queries)
        corpus = Corpus(c)
        searcher = Searcher(Collection(corpus.works))
        results = searcher.search(q)
        assert results.count == n
