#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `cylleneus` package."""

import unittest
from random import choice
import codecs
import pathlib
import lxml.etree as et

from engine.analysis.tokenizers import CachedPerseusTEITokenizer


class TestPerseusTEITokenizer(unittest.TestCase):
    """Tests for `cylleneus` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_perseus_json_tokenizer(self):
        """Test the Perseus TEI XML tokenizer."""

        perseus = pathlib.Path('text/perseus-tei/data/')
        files = perseus.glob('*/*/*lat*.xml')

        with codecs.open(choice(files), 'rb') as f:
            value = f.read()

            parser = et.XMLParser(encoding='UTF-8')
            doc = et.XML(value, parser=parser)
            divs = { i: div.get('n').lower()
                     for i, div in enumerate(doc.find(".//{http://www.tei-c.org/ns/1.0}refsDecl[@n='CTS']").findall('.//{http://www.tei-c.org/ns/1.0}cRefPattern')) if div.get('n') if div is not None }
            meta = '-'.join(divs.values())
        T = CachedPerseusTEITokenizer()

        for t in T({'text': doc, 'meta': meta}):
            assert t
