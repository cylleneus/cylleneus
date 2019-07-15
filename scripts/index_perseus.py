import pathlib
from index import Indexer
from corpus import Corpus


if __name__ == '__main__':
    perseus = pathlib.Path('index/texts/perseus/')
    indexer = Indexer(Corpus('perseus'))
    indexer.destroy()

    indexer.add(perseus)
