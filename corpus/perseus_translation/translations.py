from corpus import Corpus
from search import Searcher, Collection
from greekwordnet import GreekWordNet
import codecs
import lxml.etree as et
from pathlib import Path
from utils import nrange
from itertools import chain

if __name__ == "__main__":
    GWN = GreekWordNet()

    target = input("Find instances where the English word: ")
    lemma = input("...translates Greek: ")

    q = f'<{target}>'
    c = Corpus("perseus_translation")
    s = Searcher(Collection(c.works))
    search = s.search(q)

    results = []
    for i, hlite in enumerate(search.highlights):
        if target in hlite.text:
            results.append((search.results[i], hlite))

    for (hit, meta, _), hlite in results:
        try:
            start, end = meta["start"]["align"].split('-')
        except ValueError:
            start = end = meta["start"]["align"]

        author_code, title_code, _ = hit["urn"].split(':')[-1].split('.')

        files = list(Path("source").glob(f"{author_code}.{title_code}*.xml"))
        if files:
            file = files[0]
        else:
            file = None
        if file:
            with codecs.open(file, 'rb') as fp:
                value = fp.read()
            parser = et.XMLParser(encoding='utf-8')
            doc = et.XML(value, parser=parser)

            tokens = [t
                      for ref in nrange(start.split('.'), end.split('.'))
                      for t in doc.findall(".//t[@p='{}']".format('.'.join([str(n) for n in ref])))
                      ]

            for token in tokens:
                l1 = token.find('l').find('l1')

                if l1 is not None:
                    if l1.text == lemma:
                        print(hlite.author, hlite.title, token.get('p'), hlite.text)
