#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `cylleneus` package."""

import unittest
from random import choice
import codecs
import pathlib
import lxml.etree as et


class TestPROIELTokenizer(unittest.TestCase):
    """Tests for `cylleneus` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_proiel_tokenizer(self):
        """Test the PROIEL tokenizer."""
        pass
        # from corpus.proiel.tokenizer import CachedTokenizer
        # from corpus.proiel import AUTHOR_TAB
        #
        # proiel = pathlib.Path('corpus/proiel/text')
        # files = list(proiel.glob('*.xml'))
        #
        # with codecs.open(choice(files), 'rb') as f:
        #     value = f.read()
        #
        #     parser = et.XMLParser(encoding='UTF-8')
        #     doc = et.XML(value, parser=parser)
        #
        #     _author = doc.find('source').find('author').text
        #     _title = doc.find('source').find('title').text
        #
        #     meta = AUTHOR_TAB[_author]['works'][_title]['meta']
        #     data = {'text': doc, 'meta': meta}
        #
        # T = CachedTokenizer()
        #
        # for t in T(data, docix=0):
        #     assert t
