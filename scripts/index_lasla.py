import pathlib
from index import Indexer
from corpus import Corpus
from cylleneus import config

if __name__ == '__main__':
    lasla = pathlib.Path(config.ROOT_DIR / '/index/texts/lasla/')
    indexer = Indexer(Corpus('lasla'))
    indexer.add(lasla)
