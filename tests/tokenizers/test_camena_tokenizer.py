#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `cylleneus` package."""

import unittest
from random import choice
import codecs
from pathlib import Path
import lxml.etree as et
from cylleneus.corpus.lat.camena.tokenizer import CachedTokenizer
from cylleneus.settings import CORPUS_DIR


class TestCAMENATokenizer(unittest.TestCase):
    """Tests for `cylleneus` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_camena_tokenizer(self):
        """Test the CAMENA tokenizer."""

        # pass
        camena = CORPUS_DIR / Path("lat/camena/text")
        files = list(camena.glob('*.xml'))

        with codecs.open(choice(files), "rb") as fp:
            value = fp.read()
        parser = et.XMLParser(encoding="utf-8")
        doc = et.XML(value, parser=parser)

        divs = ["div1", "div2", "div3", "div4", "div5"]
        body = doc.find("text").find("body")

        meta = "-".join(
            [
                body.xpath("/".join(divs[: i + 1]))[0].get("type")
                for i in range(len(divs))
                if len(body.xpath("/".join(divs[: i + 1]))) != 0
            ]
        )

        T = CachedTokenizer()
        for t in T({"text": doc, "meta": meta}, mode='index', docix=0):
            assert t
