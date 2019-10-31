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

        for language in ["common", "latin", "italian", "spanish", "french", "hebrew"]:
            compile(language, overwrite=False)

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_query_types(self):
        """Test permissible query types."""

        queries = [
            ("perseus", "(<gelidus> OR <gelida>) AND <pruina>", (1, 1, 1)),
            ("perseus", "(<gelidus> OR <gelida>) THEN <pruina>", (0, 0, 0)),
            ("lasla", "'sed'", (235, 2, 1)),
            ("lasla", ":ACC.PL.", (3148, 2, 1)),
            ("latin_library", "<habeo>", (134, 6, 1)),
            ("lasla", "<animus>|ABL.SG.", (33, 2, 1)),
            ("perseus", "[en?war]", (2, 1, 1)),
            ("lasla", "[it?guerra]", (308, 2, 1)),
            ("lasla", "[en?courage]|ABL.PL.", (10, 2, 1)),
            ("latin_library", "{611}", (1975, 6, 1)),
            ("perseus", '"cum clamore"', (0, 0, 0)),
            ("perseus", '"cum <clamor>"', (0, 0, 0)),
            ("perseus", '"cum <clamor>|ABL."', (0, 0, 0)),
            ("perseus", '"cum magno calore"', (0, 0, 0)),
            ("perseus", '"cum magno" <calor>', (0, 0, 0)),
            ("lasla", '":VB. milites"', (8, 2, 1)),
            ("lasla", '":VB. <miles>"', (10, 2, 1)),
            ("perseus", "</::bellum>", (2, 1, 1)),
            ("lasla", "[!::en?cowardice]", (272, 2, 1)),
            ("latin_library", "[@::n#04478900]", (24, 6, 1)),
            ("agldt", "opt*", (8, 1, 1)),
            ("proiel", '"maled* contum*"', (1, 1, 1)),
            ("proiel", "maled* contum*", (1, 1, 1)),
            ("perseus_xml", '"<rideo> me*"', (1, 1, 1)),
            ("lasla", "/ablative absolute/", (1532, 2, 1)),
            ("lasla", "/interrogative/", (60, 2, 1)),
            ("lasla", "/QVOMINVS/", (8, 2, 1)),
            ("agldt", "/predicate/", (184, 1, 1)),
            ("agldt", "/subordinating conjunction/", (227, 1, 1)),
            ("proiel", "/adverbial/", (1410, 1, 1)),
            ("proiel", "/adnominal argument/", (167, 1, 1)),
        ]
        for c, q, n in queries:
            corpus = Corpus(c)
            clct = Collection(corpus.works)
            searcher = Searcher(Collection(clct))
            results = searcher.search(q)
            print(c, q, n, results.count)
