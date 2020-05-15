#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `cylleneus` package."""

import unittest
from random import choice
import codecs
import pathlib
import lxml.etree as et


class TestPerseusXMLLemmatizer(unittest.TestCase):
    """Tests for `cylleneus` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_perseux_xml_lemmatizer(self):
        """Test Perseus XML lemmatization."""

        from corpus.perseus_xml.tokenizer import CachedTokenizer
        from cylleneus.engine.analysis.filters import CachedLemmaFilter
        from corpus.phi5 import AUTHOR_TAB

        perseus_xml = pathlib.Path("../../corpus/perseus_xml/text/")
        files = list(perseus_xml.glob("*.xml"))
        file = choice(files)

        auth_code, work_code, _, _ = file.name.split(".")
        urn = "urn:cts:latinLit:" + f"{auth_code}.{work_code}"
        author = AUTHOR_TAB[auth_code]["author"]
        title = AUTHOR_TAB[auth_code]["works"][work_code]["title"]

        with codecs.open(file, "rb") as f:
            value = f.read()
        parser = et.XMLParser(encoding="utf-8")

        doc = et.XML(value, parser=parser)

        divs = [
            cref.get("n")
            for cref in reversed(
                doc.findall(".//{http://www.tei-c.org/ns/1.0}cRefPattern")
            )
        ]
        meta = "-".join(divs)

        data = {"text": doc, "meta": meta}

        T = CachedTokenizer()
        L = CachedLemmaFilter()
        for t in L(T(data, docix=0, mode="index")):
            print(t)
