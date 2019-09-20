from pathlib import Path

from corpus import Corpus, Work


if __name__ == '__main__':
    perseus_xml = Corpus('perseus_xml')
    path = Path('../corpus/perseus_xml/text/')
    for file in path.glob('*lat?.xml'):
        w = Work(corpus=perseus_xml)
        w.indexer.from_file(file)
