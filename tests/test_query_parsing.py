#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `cylleneus` package."""


import unittest


class TestQueryParsing(unittest.TestCase):
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

    def test_query_parsing(self):
        """Test query parsing."""

        from cylleneus.corpus import Corpus
        from cylleneus.engine.qparser.default import CylleneusQueryParser

        queries = [
            ("perseus", "{=Anatomy}"),
            ("dcs", "[=the Sustainer]"),
            ("perseus", "(<gelidus> OR <gelida>) AND <pruina>"),
            ("latin_library", "'sed'"),
            ("proiel", ":ACC.PL."),
            ("proiel", "<habeo>"),
            ("agldt", "<animus>|ABL.SG."),
            ("camena", "[en?war]"),
            ("camena", "[it?guerra]"),
            ("digiliblt", "{611}"),
            ("perseus", '"cum clamore"'),
            ("perseus", '"cum <clamor>"'),
            ("perseus", '"cum <clamor>|ABL."'),
            ("perseus", '"cum magno" <calor>'),
            ("lasla", '":VB. milites"'),
            ("lasla", '":VB. <miles>"'),
            ("proiel", "</::bellum>"),
            ("latin_library", "[!::en?cowardice]"),
            ("perseus_xml", "[en?courage]|ABL.PL."),
            ("perseus", "[@::n#04478900]"),
            ("latin_library", "opt*"),
            ("atlas", "<τεύχω>"),
            ("diorisis", "<Σωκράτης>"),
            ("lasla", "/ablative absolute/"),
            ("lasla", "/interrogative/"),
            ("lasla", "/QVOMINVS/"),
            ("proiel", "/predicate/"),
            ("lasla", "/subordinating conjunction/"),
            ("proiel", "/adverbial/"),
            ("proiel", "/adnominal argument/"),
        ]

        for corpus, query in queries:
            c = Corpus(corpus)
            p = CylleneusQueryParser("form", c.schema)
            q = p.parse(query)
            assert q
