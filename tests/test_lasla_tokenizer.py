#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `cylleneus` package."""


import unittest
import codecs
import pathlib
from corpus.utils.lasla import FILE_TAB, AUTHOR_TAB
import re
from engine.analysis.tokenizers import CachedLASLATokenizer
from random import choice


class TestLASLATokenizer(unittest.TestCase):
    """Tests for `cylleneus` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_lasla_tokenizer(self):
        """Test the LASLA tokenizer."""
        pass
        # lasla = pathlib.Path('text/lasla/')
        # files = list(lasla.glob('*.BPN'))
        #
        # with codecs.open(choice(files), 'r', 'utf8') as f:
        #     doc = f.readlines()
        #
        # file_author, file_title, abbrev = file.name.rstrip('.BPN').split('_')
        #
        # uids = FILE_TAB[file_author][file_title]
        # if len(uids) > 1 and abbrev[-1].isdigit():
        #     i = int(re.search(r"(\d+)$", abbrev).group(1)) - 1
        #     uid = uids[i]
        # else:
        #     uid = uids[0]
        # author = AUTHOR_TAB[uid[0]]['author']
        # codes = AUTHOR_TAB[uid[0]]['code']
        # for code in codes:
        #     if uid[1:] in AUTHOR_TAB[uid[0]][code]:
        #         joined_code = code + '.' + AUTHOR_TAB[uid[0]][code][uid[1:]]['code']
        #         title = AUTHOR_TAB[uid[0]][code][uid[1:]]['title']
        #         meta = AUTHOR_TAB[uid[0]][code][uid[1:]]['meta']
        #
        # T = CachedLASLATokenizer()
        # for t in T({"text": doc, "meta": meta}, mode='index'):
        #     assert t
