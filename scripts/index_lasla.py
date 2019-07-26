import pathlib

from corpus import Corpus
from index import Indexer

if __name__ == '__main__':
    lasla = pathlib.Path('corpus/lasla/text/')
    indexer = Indexer(Corpus('lasla'))
    indexer.destroy()

    indexer.add(lasla)
