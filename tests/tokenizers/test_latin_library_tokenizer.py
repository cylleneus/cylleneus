#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `cylleneus` package."""

import unittest
from random import choice
import codecs
import pathlib
import re


class TestPlaintextTokenizer(unittest.TestCase):
    """Tests for `cylleneus` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_plaintext_tokenizer(self):
        """Test the plaintext tokenizer."""

        # from corpus.default import CachedTokenizer
        # latin_library = pathlib.Path('../../corpus/latin_library/text/')
        # files = list(latin_library.glob('*/*.txt'))
        #
        # with codecs.open(choice(files), 'r', 'utf8') as fp:
        #     doc = fp.read()
        #
        # # Clean the text
        # doc = re.sub(r'(\s)+', r'\1', doc)
        #
        # T = CachedTokenizer()
        #
        # for t in T(doc, docix=0):
        #     assert t
