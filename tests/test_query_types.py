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
            ("lasla", "'sed'", (234, 2, 1)),
            ("lasla", ":ACC.PL.", (2679, 2, 1)),
            ("latin_library", "<habeo>", (121, 6, 1)),
            ("lasla", "<animus>|ABL.SG.", (55, 2, 1)),
            ("perseus", "[en?war]", (206, 3, 1)),
            ("lasla", "[it?guerra]", (300, 2, 1)),
            ("lasla", "[en?courage]|ABL.PL.", (10, 2, 1)),
            ("latin_library", "{611}", (273, 6, 1)),
            ("perseus", '"cum clamore"', (2, 2, 1)),
            ("perseus", '"cum <clamor>"', (3, 2, 1)),
            ("perseus", '"cum <clamor>|ABL."', (2, 2, 1)),
            ("perseus", '"cum magno" <calor>', (1, 2, 1)),
            ("lasla", '":VB. milites"', ()),
            ("lasla", '":VB. <miles>"', ()),
            ("latin_library", "</::bellum>", (14, 5, 1)),
            ("perseus", "[!::en?love]", (53, 3, 1)),
            ("latin_library", "[@::n#04478900]", (20, 6, 1)),
        ]
        c, q, n = choice(queries)
        corpus = Corpus(c)
        searcher = Searcher(Collection(list(corpus.works)))
        results = searcher.search(q)
        assert results.count == n
