import codecs
from datetime import datetime
from pathlib import Path

import lxml.etree as et
from cylleneus.corpus.lat.phi5 import AUTHOR_TAB
from cylleneus.corpus.preprocessing import BasePreprocessor


class Preprocessor(BasePreprocessor):
    def parse(self, file: Path):
        with codecs.open(file, "rb") as f:
            value = f.read()
        parser = et.XMLParser(encoding="utf-8")
        doc = et.XML(value, parser=parser)

        urn = doc.get("cts")

        auth_code, work_code = urn.rsplit(":", maxsplit=1)[1].split(".")[:2]

        author = AUTHOR_TAB[auth_code]["author"]
        title = AUTHOR_TAB[auth_code]["works"][work_code]["title"]
        meta = AUTHOR_TAB[auth_code]["works"][work_code]["meta"]

        data = {"text": doc, "meta": meta}

        return {
            "urn":          urn,
            "author":       author,
            "title":        title,
            "language":     "lat"
                            if doc.get("{http://www.w3.org/XML/1998/namespace}lang") == "la"
                            else "grk",
            "meta":         meta,
            "form":         data,
            "lemma":        data,
            "synset":       data,
            "annotation":   data,
            "semfield":     data,
            "morphosyntax": data,
            "filename":     file.name,
            "datetime":     datetime.now(),
        }
