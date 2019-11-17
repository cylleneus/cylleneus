#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `cylleneus` package."""

import unittest
from random import choice
import codecs
import pathlib
import lxml.etree as et


class TestPerseusXMLTokenizer(unittest.TestCase):
    """Tests for `cylleneus` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_perseus_xml_tokenizer(self):
        """Test the Perseus translation XML okenizer."""
        from corpus.translation_alignments.tokenizer import CachedTokenizer

        translations = pathlib.Path('../../corpus/translation_alignments/text/')
        files = list(translations.glob('*.txt'))

        with codecs.open(choice(files), 'rb') as f:
            value = f.read()

            parser = et.XMLParser(encoding='UTF-8')
            doc = et.XML(value, parser=parser)
            divs = {i: div.get('n').lower()
                    for i, div in enumerate(doc.find(".//{http://www.tei-c.org/ns/1.0}refsDecl[@n='CTS']").findall(
                    './/{http://www.tei-c.org/ns/1.0}cRefPattern')) if div.get('n') if div is not None}
            meta = '-'.join((list(divs.values())))

        T = CachedTokenizer()

        for t in T({'text': doc, 'meta': meta}, docix=0, mode='index'):
            print(t)
