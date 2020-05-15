#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `cylleneus` package."""

import codecs
from pathlib import Path
import unittest
from random import choice

from cylleneus.settings import CORPUS_DIR


class TestDCSLemmatizer(unittest.TestCase):
    """Tests for `cylleneus` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_dcs_lemmatizer(self):
        """Test the DCS lemmatizer."""

        from cylleneus.corpus.skt.dcs.tokenizer import CachedTokenizer
        from cylleneus.corpus.skt.dcs.filters import CachedLemmaFilter

        dcs = CORPUS_DIR / Path("skt/dcs/text")
        files = list(dcs.glob("*.conllu"))

        with codecs.open(choice(files), "r", "utf8") as file:
            doc = file.readlines()
        meta = "chapter-line"

        T = CachedTokenizer()
        L = CachedLemmaFilter()
        for t in L(T({"data": doc, "meta": meta}, mode="index", docix=0)):
            assert t
