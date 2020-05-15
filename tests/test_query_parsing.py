#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `cylleneus` package."""


import unittest
from random import choice

from cylleneus import settings
from cylleneus.corpus import Corpus
from cylleneus.search import Searcher, Collection
from cylleneus.engine.qparser.default import CylleneusQueryParser
from cylleneus.corpus.default import DocumentSchema


class TestQueryTypes(unittest.TestCase):
    """Tests for `cylleneus` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

        from multiwordnet.db import compile

        for language in [
            "common",
            "latin",
            "italian",
            "spanish",
            "french",
            "hebrew",
        ]:
            compile(language, overwrite=False)

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_query_types(self):
        """Test permissible query types."""

        queries = [
            "(<gelidus> OR <gelida>) AND <pruina>",
            "(<gelidus> OR <gelida>) THEN <pruina>",
            "'sed'",
            ":ACC.PL.",
            "<habeo>",
            "<animus>|ABL.SG.",
            "[en?war]",
            "[it?guerra]",
            "{611}",
            '"cum clamore"',
            '"cum <clamor>"',
            '"cum <clamor>|ABL."',
            '"cum magno calore"',
            '"cum magno" <calor>',
            '":VB. milites"',
            '":VB. <miles>"',
            "</::bellum>",
            "[!::en?cowardice]",
            "[en?courage]|ABL.PL.",
            "[@::n#04478900]",
            "opt*",
            '"maled* contum*"',
            "maled* contum*",
            '"<rideo> me*"',
            "/ablative absolute/",
            "/interrogative/",
            "/QVOMINVS/",
            "/predicate/",
            "/subordinating conjunction/",
            "/adverbial/",
            "/adnominal argument/",
        ]

        for q in queries:
            parser = CylleneusQueryParser("form", DocumentSchema())
            query = parser.parse(q, debug=settings.DEBUG)
            assert query
