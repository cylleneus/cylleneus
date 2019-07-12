import pathlib
from index import Indexer
from corpus import Corpus


if __name__ == '__main__':
    lasla = pathlib.Path('../corpus/text/lasla/')
    indexer = Indexer(Corpus('lasla'))
    indexer.add(lasla)
