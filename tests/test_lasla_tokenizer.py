#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `cylleneus` package."""


import unittest


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
        # with codecs.open(choice(files), 'r', 'utf8') as file:
        #     doc = file.readlines()
        #
        # filename = pathlib.Path(file.name).name
        # file_author, file_title, abbrev = filename.rstrip('.BPN').split('_')
        #
        # uids = corpus.lasla.FILE_TAB[file_author][file_title]
        # if len(uids) > 1 and abbrev[-1].isdigit():
        #     i = int(re.search(r"(\d+)$", abbrev).group(1)) - 1
        #     uid = uids[i]
        # else:
        #     uid = uids[0]
        # codes = corpus.lasla.AUTHOR_TAB[uid[0]]['code']
        # for code in codes:
        #     if uid[1:] in corpus.lasla.AUTHOR_TAB[uid[0]][code]:
        #         meta = corpus.lasla.AUTHOR_TAB[uid[0]][code][uid[1:]]['meta']
        #
        # T = CachedLASLATokenizer()
        # for t in T({"text": doc, "meta": meta}, mode='index'):
        #     assert t
