#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `cylleneus` package."""

import unittest
from random import choice
import codecs
import pathlib
import re

from engine.analysis.tokenizers import CachedPlainTextTokenizer


class TestPlaintextTokenizer(unittest.TestCase):
    """Tests for `cylleneus` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_plaintext_tokenizer(self):
        """Test the plaintext tokenizer."""
        pass
        # latin_library = pathlib.Path('tests/text/latin_library/')
        # files = list(latin_library.glob('*.txt'))
        #
        # with codecs.open(choice(files), 'r', 'utf8') as fp:
        #     doc = fp.read()
        #
        # # Clean the text
        # doc = re.sub(r"\.,", ".", doc)
        # doc = re.sub(r"([\w])\.([\w])", r"\1. \2", doc)
        # doc = re.sub(r",([\w])", r", \1", doc)
        # doc = re.sub(r"(?<=\w)\.\.", r" . .", doc)
        # doc = re.sub(r"([.,;:])([.,;:])", r"\1 \2", doc)
        # doc = re.sub(r"[\t\r\n ]+", " ", doc)
        # doc = re.sub(r'\.\"', '\"\.', doc)
        # doc = re.sub(r' ,', ',', doc)
        # doc = re.sub(r'\[ \d+ \] ', '', doc)
        # doc = re.sub(r' \[,', '[,', doc)
        # doc = re.sub(r'\]\.', '.]', doc)
        #
        # T = CachedPlainTextTokenizer()
        #
        # for t in T(doc, docix=0):
        #     assert t
