#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `cylleneus` package."""

import codecs
from pathlib import Path
import unittest
from random import choice

from cylleneus.settings import CORPUS_DIR


class TestDCSTokenizer(unittest.TestCase):
    """Tests for `cylleneus` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_dcs_tokenizer(self):
        """Test the DCS tokenizer."""

        from cylleneus.corpus.skt.dcs.tokenizer import CachedTokenizer
        dcs = CORPUS_DIR / Path("skt/dcs/text")
        files = list(dcs.glob('*.conllu'))

        with codecs.open(choice(files), 'r', 'utf8') as file:
            doc = file.readlines()
        meta = "chapter-line"

        T = CachedTokenizer()
        for t in T({"text": doc, "meta": meta}, mode='index', docix=0):
            print(t)
