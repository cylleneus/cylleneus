#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `cylleneus` package."""

import unittest
import pathlib
import codecs
from random import choice
import lxml.etree as et


class TestPerseusTranslationLemmatization(unittest.TestCase):
    """Tests for `cylleneus` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_perseus_json_tokenizer(self):
        """Test Perseus JSON lemmatization."""
        from translation.corpus.perseus_translation.tokenizer import CachedTokenizer
        from translation.corpus.perseus_translation.filters import CachedLemmaFilter

        perseus = pathlib.Path('../../translation/corpus/perseus/text/')
        files = list(perseus.glob('*.xml'))

        with codecs.open(choice(files), 'rb') as f:
            value = f.read()

            parser = et.XMLParser(encoding='UTF-8')
            doc = et.XML(value, parser=parser)
            divs = {i: div.get('n').lower()
                    for i, div in enumerate(doc.find(".//{http://www.tei-c.org/ns/1.0}refsDecl[@n='CTS']").findall(
                    './/{http://www.tei-c.org/ns/1.0}cRefPattern')) if div.get('n') if div is not None}
            meta = '-'.join((list(divs.values())))

        tokens = CachedTokenizer()
        lemmas = CachedLemmaFilter()
        for t in lemmas(tokens({'text': doc, 'meta': meta}, docix=0, mode='index')):
            print(t)
