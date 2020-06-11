import codecs
from datetime import datetime
from pathlib import Path

import lxml.etree as et

from cylleneus.corpus.grk.tlg import AUTHOR_TAB
from cylleneus.corpus.preprocessing import BasePreprocessor


class Preprocessor(BasePreprocessor):
    def parse(self, file: Path):
        with codecs.open(file, "rb") as f:
            value = f.read()
        parser = et.XMLParser(encoding="utf-8")
        doc = et.XML(value, parser=parser)

        titleStmt = doc.find('.//teiHeader').find('fileDesc').find('titleStmt')
        auth_code = f"tlg{titleStmt.find('tlgAuthor').text}"
        work_code = f"tlg{titleStmt.find('tlgId').text}"

        meta = AUTHOR_TAB[auth_code]["works"][work_code]["meta"]

        profileDesc = doc.find('.//teiHeader').find('profileDesc')
        xenoData = doc.find('.//teiHeader').find('xenoData')

        return {
            "author":     titleStmt.find('author').text,
            "title":      titleStmt.find('title').text,
            "date":       profileDesc.find('creation').find('date').text,
            "genre":      xenoData.find('genre').text,
            "subgenre":   xenoData.find('subgenre').text,
            "language":   "grk",
            "meta":       meta,
            "urn":        f"urn:cts:greekLit:{auth_code}.{work_code}",
            "form":       doc,
            "lemma":      doc,
            "synset":     doc,
            "annotation": doc,
            "semfield":   doc,
            "filename":   file.name,
            "datetime":   datetime.now(),
        }
