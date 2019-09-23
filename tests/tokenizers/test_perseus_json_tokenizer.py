#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `cylleneus` package."""

import unittest
import pathlib
import codecs
from random import choice
import json


class TestPerseusJSONTokenizer(unittest.TestCase):
    """Tests for `cylleneus` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_perseus_json_tokenizer(self):
        """Test the Perseus JSON tokenizer."""
        pass
        # from corpus.perseus.tokenizer import CachedTokenizer
        #
        # perseus = pathlib.Path('../corpus/perseus/text')
        # files = list(perseus.glob('*eclogues__latin.json'))
        #
        # with codecs.open(choice(files), 'r', 'utf8') as f:
        #     data = json.load(f)
        #
        # divs = data['meta'].split('-')
        #
        # T = CachedTokenizer()
        #
        # for t in T(value=data, mode='index', docix=0):
        #     assert t

