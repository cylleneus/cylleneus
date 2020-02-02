#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `cylleneus` package."""

import unittest
from random import choice
import codecs
import pathlib
import lxml.etree as et


class TestRamsesTokenizer(unittest.TestCase):
    """Tests for `cylleneus` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_ramses_tokenizer(self):
        """Test the Ramses tokenizer."""

        from cylleneus.corpus.ramses.tokenizer import CachedTokenizer
        from cylleneus.corpus import Corpus

        ramses = Corpus("ramses")
        files = list(ramses.text_dir.glob(ramses.glob))

        with codecs.open(choice(files), 'rb') as f:
            value = f.read()

            parser = et.XMLParser(encoding='UTF-8')
            doc = et.XML(value, parser=parser)

            urn = doc.find('head').findall('referenceSystem')[0].get("sourceName")
            author = "Amenemope"
            title = "Instructions"
            meta = "page-line"

            data = {'text': doc, 'meta': meta}

        T = CachedTokenizer()

        for t in T(data, docix=0):
            print(t)
