import codecs
from datetime import datetime
from pathlib import Path

import lxml.etree as et

from cylleneus.corpus.preprocessing import BasePreprocessor


class Preprocessor(BasePreprocessor):
    def parse(self, file: Path):
        with codecs.open(file, "rb") as f:
            value = f.read()
        parser = et.XMLParser(encoding="utf-8")
        doc = et.XML(value, parser=parser)

        urn = doc.xpath(
            "teiHeader/fileDesc/publicationStmt/address/addrLine/anchor"
        )[0].get("n")

        author = doc.xpath("teiHeader/fileDesc/titleStmt/author")[0].text
        title = doc.xpath("teiHeader/fileDesc/titleStmt/title")[0].text.split(
            ":"
        )[0]
        divs = ["div1", "div2", "div3", "div4", "div5"]
        body = doc.find("text").find("body")
        meta = "-".join(
            [
                body.xpath("/".join(divs[: i + 1]))[0].get("type")
                for i in range(len(divs))
                if len(body.xpath("/".join(divs[: i + 1]))) != 0
            ]
        )

        data = {"text": doc, "meta": meta}

        return {
            "urn":        urn,
            "author":     author,
            "title":      title,
            "language":   "lat",
            "meta":       meta,
            "form":       data,
            "lemma":      data,
            "synset":     data,
            "annotation": data,
            "semfield":   data,
            "filename":   file.name,
            "datetime":   datetime.now(),
        }
