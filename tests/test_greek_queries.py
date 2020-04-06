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
            ("atlas", "<βασιλεύς>", (64, 3, 1)),
            ("atlas", "'βασιλῆϊ'", (7, 2, 1)),
            ("atlas", "<βασιλεύς>|DAT.SG.", (7, 2, 1)),
            ("atlas", "[en?king]", (1298, 3, 1)),
            ("atlas", "[en?king]|DAT.SG.", (64, 3, 1)),
            ("atlas", "[n#07354565]", (771, 3, 1)),
            ("atlas", "<νόσος> AND 'στρατὸν'", (1, 1, 1)),
            ("atlas", "<νόσος> THEN <ἀνά>", (1, 1, 1)),
            ("atlas", ":DAT.SG.", (3071, 3, 1)),
            ("atlas", "[it?guerra]", (849, 3, 1)),
        ]
        c, q, n = choice(queries)
        corpus = Corpus(c)
        clct = Collection(works=corpus.works)
        searcher = Searcher(Collection(works=clct))
        results = searcher.search(q)
        # assert results.count == n
        for hlite in results.highlights:
            print(hlite)
