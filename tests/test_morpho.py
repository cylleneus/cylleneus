#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `cylleneus` package."""


import unittest
import codecs
import pathlib
from engine.analysis.tokenizers import CachedLASLATokenizer
from engine.analysis.analyzers import CompositeAnalyzer
from engine.analysis.filters import CachedLASLALemmaFilter, AnnotationFilter
from index.preprocessing import LASLAPreprocessor


class TestLASLATokenizer(unittest.TestCase):
    """Tests for `cylleneus` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_lasla_annotations(self):
        """Test the annotation pipeline using a sample text from LASLA corpus."""

        file = pathlib.Path('text/lasla/Catullus_Catullus_Catul.BPN')
        if file.exists():
            doc = LASLAPreprocessor().parse(file)

            analyzer = CompositeAnalyzer() | CachedLASLATokenizer() | CachedLASLALemmaFilter() | AnnotationFilter()
            for token in analyzer(doc['annotation'], mode='index'):
                assert token
