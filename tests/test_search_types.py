#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `cylleneus` package."""

import unittest


class TestSearchTypes(unittest.TestCase):
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

    def test_search_types(self):
        """Test search types."""

        from cylleneus.corpus import Corpus
        from cylleneus.search import Collection, Searcher

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
            ("latin_library", "</::bellum>"),
            ("latin_library", "[!::en?cowardice]"),
            ("latin_library", "[en?courage]|ABL.PL."),
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
            if not c.searchable:
                c.download()
            s = Searcher(collection=Collection(works=c.works))
            r = s.search(query)
            assert r
