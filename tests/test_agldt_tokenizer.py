#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `cylleneus` package."""

import unittest
from random import choice
import codecs
import pathlib
import lxml.etree as et

from engine.analysis.tokenizers import CachedPerseusTEITokenizer


class TestPROIELTokenizer(unittest.TestCase):
    """Tests for `cylleneus` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_proiel_tokenizer(self):
        """Test the AGLDT tokenizer."""
        from engine.analysis.tokenizers import CachedAGLDTTokenizer
        from corpus.phi5 import AUTHOR_TAB

        agldt = pathlib.Path('../corpus/agldt/text')
        files = list(agldt.glob('*.txt'))

        with codecs.open(choice(files), 'rb') as f:
            value = f.read()

            parser = et.XMLParser(encoding='UTF-8')
            doc = et.XML(value, parser=parser)

            urn = doc.get('cts')
            auth_code, work_code = urn.rsplit(':', maxsplit=1)[1].split('.')[:2]
            meta = AUTHOR_TAB[auth_code]['works'][work_code]['meta']

            data = {'text': doc, 'meta': meta}

        T = CachedAGLDTTokenizer()

        for t in T(data, docix=0):
            print(t)
