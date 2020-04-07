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
            ("dcs", "<deva>", (7, 1, 1)),
            ("dcs", "'saṃkrīḍamānaḥ'", (1, 1, 1)),
            ("dcs", "<svāpa>|ACC.SG.", (1, 1, 1)),
            ("dcs", "[en?praise]", (3, 1, 1)),
            ("dcs", "[en?praise]|ACC.PL.", (0, 0, 0)),
            ("dcs", "[en?praise]|INS.SG.", (1, 1, 1)),
            ("dcs", "[n#07354565]", (1, 1, 1)),
            ("dcs", "<kāma> AND 'śivaśiva'", (1, 1, 1)),
            ("dcs", "<māsa> THEN <kathaṃcid>", (7, 3, 1)),
            ("dcs", ":GEN.PL.", (107, 4, 1)),
            ("dcs", "[it?re]", (1, 1, 1))
        ]
        for c, q, n in queries:
            corpus = Corpus(c)
            if not corpus.is_searchable:
                corpus.download()
            clct = Collection(works=corpus.works)
            searcher = Searcher(Collection(works=clct))
            results = searcher.search(q)
            assert results.count == n
