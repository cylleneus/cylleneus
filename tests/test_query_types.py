#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `cylleneus` package."""


import unittest
from random import choice

from corpus import Corpus
from search import Searcher


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
            "'sed'",
            ":ACC.PL.",
            "<habeo>",
            "<animus>:SG.ABL.",
            "[en?war]",
            "[it?guerra]",
            "[es?guerra]",
            "[fr?guerre]",
            "[en?courage]:GEN.SG.",
            "{611}",
            '"cum <virtus>"',
            '"cum <virtus>:SG."',
            ":VB. 'milites'",
            ":VB. <miles>",
            "</=bellum>",
            "[!=en?love]",
            "[@=n#04478900]",
        ]

        c = Corpus(choice(['lasla', 'perseus', 'latin_library']))
        e = Searcher(c)

        results = list(e.search(choice(queries), debug=False).results)
        assert results is not None
