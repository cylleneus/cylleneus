#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `cylleneus` package."""

import unittest
from random import choice

from cylleneus.corpus import Corpus
from cylleneus.search import Searcher, Collection


class TestGreekQueryTypes(unittest.TestCase):
    """Tests for `cylleneus` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

        from multiwordnet.db import compile

        for language in ["common", "latin", "italian", "spanish", "french", "hebrew"]:
            compile(language, overwrite=False)

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_query_types(self):
        """Test permissible query types for Greek."""

        queries = [
            ("dcs", "<deva>", (64, 3, 1)),
            ("dcs", "'tadantareṇa'", (7, 2, 1)),
            ("dcs", "<deva>|GEN.PL.", (7, 2, 1)),
            ("dcs", "[en?woman]", (1298, 3, 1)),
            ("dcs", "[en?woman]|DAT.PL.", (64, 3, 1)),
            ("dcs", "[en?woman]|DAT.SG.", (64, 3, 1)),
            ("dcs", "[n#07354565]", (771, 3, 1)),
            ("dcs", "<avama> AND 'viṣṇuḥ'", (1, 1, 1)),
            ("dcs", "<devatā> THEN <viṣṇu>", (1, 1, 1)),
            ("dcs", ":GEN.PL.", (3071, 3, 1)),
            ("dcs", "[it?re]", (849, 3, 1)),
        ]
        for c, q, n in queries:
            corpus = Corpus(c)
            clct = Collection(works=corpus.works)
            searcher = Searcher(Collection(works=clct))
            results = searcher.search(q)
            print(c, q, n, results.count, list(results.highlights))
