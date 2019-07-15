import pathlib
from index import Indexer
from corpus import Corpus
import config

if __name__ == '__main__':
    perseus = pathlib.Path(config.ROOT_DIR / '/index/texts/perseus/')
    indexer = Indexer(Corpus('perseus'))
    indexer.add(perseus)
