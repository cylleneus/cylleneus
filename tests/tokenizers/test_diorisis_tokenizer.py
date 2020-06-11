#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `cylleneus` package."""

import unittest
from random import choice
import codecs
from pathlib import Path
import lxml.etree as et
from cylleneus.settings import CORPUS_DIR


class TestDiorisisTokenizer(unittest.TestCase):
    """Tests for `cylleneus` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_diorisis_tokenizer(self):
        """Test the Diorisis tokenizer."""

        from cylleneus.corpus.grk.diorisis import Tokenizer

        diorisis = CORPUS_DIR / Path("grk/diorisis/text")
        files = list(diorisis.glob("*.xml"))

        with codecs.open(choice(files), 'rb') as f:
            value = f.read()
        parser = et.XMLParser(encoding="utf-8")
        doc = et.XML(value, parser=parser)

        T = Tokenizer()

        for t in T(doc, docix=0, mode="index"):
            assert t
