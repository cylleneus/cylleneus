import pathlib
from index import Indexer
from corpus import Corpus


if __name__ == '__main__':
    lasla = pathlib.Path('index/texts/lasla/')
    indexer = Indexer(Corpus('lasla'))
    indexer.destroy()

    indexer.add(lasla)
