#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `cylleneus` package."""

import unittest
from random import choice
import codecs
from pathlib import Path
import lxml.etree as et
from cylleneus.corpus.lat.digiliblt.tokenizer import CachedTokenizer
from cylleneus.settings import CORPUS_DIR


class TestDigilibLTTokenizer(unittest.TestCase):
    """Tests for `cylleneus` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_digiliblt_tokenizer(self):
        """Test the DigilibLT tokenizer."""

        # pass
        EXCLUDED_TAGS = ["row"]

        dlt = CORPUS_DIR / Path("lat/digiliblt/text")
        files = list(dlt.glob("*595.xml"))

        with codecs.open(choice(files), "rb") as fp:
            value = fp.read()
        parser = et.XMLParser(encoding="utf-8")
        doc = et.XML(value, parser=parser)

        body = doc.find('{http://www.tei-c.org/ns/1.0}text').find('{http://www.tei-c.org/ns/1.0}body')
        tags = []
        for el in body.findall(".//{http://www.tei-c.org/ns/1.0}div") + body.findall(
            ".//{http://www.tei-c.org/ns/1.0}milestone"
        ):
            if el.get("n"):
                tag = el.get("type") or el.get("unit")
                if tag not in tags and tag not in EXCLUDED_TAGS:
                    tags.append(tag)

        if tags:
            meta = "-".join(tags)
        else:
            meta = "-"

        T = CachedTokenizer()
        for t in T({"text": doc, "meta": meta}, mode="index", docix=0):
            assert t
