import codecs
import pathlib
import lxml.etree as et

from engine.analysis.tokenizers import CachedPerseusTEITokenizer

if __name__=='__main__':
    perseus = pathlib.Path('../text/perseus-tei/data/phi0119/phi001/')
    files = perseus.glob('*lat*.xml')
    for file in files:
        with codecs.open(file, 'rb') as f:
            value = f.read()

            parser = et.XMLParser(encoding='UTF-8')
            doc = et.XML(value, parser=parser)
            divs = { i: div.get('n').lower()
                     for i, div in enumerate(doc.find(".//{http://www.tei-c.org/ns/1.0}refsDecl[@n='CTS']").findall('.//{http://www.tei-c.org/ns/1.0}cRefPattern')) if div.get('n') if div is not None }
            meta = '-'.join(divs.values())
        T = CachedPerseusTEITokenizer()

        for t in T({'text': doc, 'meta': meta}):
            print(t)
            # tags = ', '.join([f"{div.lower()}={t.meta[div.lower()]}" for div in divs.values()])
            # print(f"{t.startchar}-{t.original} | {t.text}-{t.endchar}\t\t{tags}")
