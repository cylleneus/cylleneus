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
            "'ius'",
            ":ACC.PL.",
            "<virtus>",
            "<animus>:PL.ABL.",
            "[en?war]",
            "[it?guerra]",
            "[es?guerra]",
            "[fr?guerre]",
            "[en?courage]:GEN.SG.",
            "{611}",
            '"cum <virtus>"',
            '"cum <virtus>:SG."',
            "'milites' :VB.",
            ":VB. 'milites'",
            ":VB. <miles>",
            "</=bellum>",
            "[!=en?love]",
            "[@=n#04478900]",
        ]

        c = Corpus(choice(['lasla', 'perseus']))
        e = Searcher(c)

        results = list(e.search(choice(queries), debug=False).results)
        assert results
