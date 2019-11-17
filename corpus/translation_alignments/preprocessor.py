import codecs
from datetime import datetime
from pathlib import Path

import lxml.etree as et
from corpus.preprocessing import BasePreprocessor


class Preprocessor(BasePreprocessor):
    def parse(self, file: Path):

        with codecs.open(file, 'rb') as f:
            value = f.read()
        parser = et.XMLParser(encoding='utf-8')

        doc = et.XML(value, parser=parser)

        author = doc.xpath(
            "/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:author",
            namespaces={
                'tei': 'http://www.tei-c.org/ns/1.0'
            }
        )[0].text
        title = doc.xpath(
            "/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title",
            namespaces={
                'tei': 'http://www.tei-c.org/ns/1.0'
            }
        )[0].text.split('.')[0]
        translator = doc.xpath(
            "/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:editor[@role='translator']",
            namespaces={
                'tei': 'http://www.tei-c.org/ns/1.0'
            }
        )
        if translator:
            translator = translator[0].text
        else:
            translator = ""
        urn = doc.find(".//{http://www.tei-c.org/ns/1.0}div[@type='translation']").get('n')

        divs = [
            cref.get('n')
            for cref in reversed(doc.findall(".//{http://www.tei-c.org/ns/1.0}cRefPattern"))
        ]
        meta = '-'.join(divs)

        data = {'text': doc, 'meta': meta}

        return {
            'urn':        urn,
            'author':     author,
            'title':      title,
            'translator': translator,
            'meta':       meta,
            'form':       data,
            'lemma':      data,
            'synset':     data,
            'semfield':   data,
            'filename':   file.name,
            'datetime':   datetime.now()
        }
