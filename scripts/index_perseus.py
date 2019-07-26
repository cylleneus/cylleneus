import pathlib

from corpus import Corpus
from index import Indexer

if __name__ == '__main__':
    perseus = pathlib.Path('corpus/perseus/texts/')
    indexer = Indexer(Corpus('perseus'))
    indexer.destroy()

    indexer.add(perseus)
