#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `cylleneus` package."""

import unittest
from random import choice
import codecs
import pathlib
import re


class TestPHI5Tokenizer(unittest.TestCase):
    """Tests for `cylleneus` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_phi5_tokenizer(self):
        """Test the PHI5 tokenizer."""
        pass
        # from corpus.phi5.tokenizer import CachedTokenizer
        # phi5 = pathlib.Path('tests/text/phi5/')
        # files = phi5.glob('*.txt')
        # with codecs.open(choice(files), 'r', 'utf8') as f:
        #     value = f.read()
        #
        # content = re.sub(r".*?\t", "", value)
        # content = re.sub(r"_", " ", content)
        # value = re.sub(r"_", " ", value)
        #
        # T = CachedTokenizer()
        # data = { 'meta': 'fragment-verse', 'text': value}
        #
        # for t in T(data, docix=0):
        #     assert t
