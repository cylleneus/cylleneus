#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `cylleneus` package."""

import unittest


class TestPerseusJSONTokenizer(unittest.TestCase):
    """Tests for `cylleneus` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_perseus_json_tokenizer(self):
        """Test the Perseus JSON tokenizer."""
        pass
        # perseus = pathlib.Path('tests/text/perseus')
        # files = list(perseus.glob('*.json'))
        #
        # with codecs.open(choice(files), 'r', 'utf8') as f:
        #     data = json.load(f)
        #
        # divs = data['meta'].split('-')
        #
        # T = CachedPerseusJSONTokenizer()
        #
        # for t in T(value=data, mode='index'):
        #     assert t
