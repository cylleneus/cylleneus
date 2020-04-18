import codecs
from datetime import datetime
from pathlib import Path

import lxml.etree as et
from cylleneus.corpus.preprocessing import BasePreprocessor

EXCLUDED_TAGS = ["row"]


class Preprocessor(BasePreprocessor):
    def parse(self, file: Path):
        with codecs.open(file, "rb") as f:
            value = f.read()
        parser = et.XMLParser(encoding="utf-8")
        doc = et.XML(value, parser=parser)

        urn = (
            doc.find("{http://www.tei-c.org/ns/1.0}teiHeader")
                .find("{http://www.tei-c.org/ns/1.0}fileDesc")
                .find("{http://www.tei-c.org/ns/1.0}publicationStmt")
                .find("{http://www.tei-c.org/ns/1.0}idno")
                .text
        )

        author_el = (
            doc.find("{http://www.tei-c.org/ns/1.0}teiHeader")
                .find("{http://www.tei-c.org/ns/1.0}fileDesc")
                .find("{http://www.tei-c.org/ns/1.0}titleStmt")
                .find("{http://www.tei-c.org/ns/1.0}author")
        )
        if author_el is not None:
            author = author_el.text if author_el.text else "-"
        else:
            author = "-"
        title_el = (
            doc.find("{http://www.tei-c.org/ns/1.0}teiHeader")
                .find("{http://www.tei-c.org/ns/1.0}fileDesc")
                .find("{http://www.tei-c.org/ns/1.0}titleStmt")
                .find("{http://www.tei-c.org/ns/1.0}title")
        )
        if title_el is not None:
            title = title_el.text if title_el.text else "-"
        else:
            title = "-"

        body = doc.find("{http://www.tei-c.org/ns/1.0}text").find(
            "{http://www.tei-c.org/ns/1.0}body"
        )
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
