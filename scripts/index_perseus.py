import pathlib

from corpus import Corpus
from index import Indexer

if __name__ == '__main__':
    perseus = pathlib.Path('corpus/perseus/text/')
    indexer = Indexer(Corpus('perseus'))
    indexer.destroy()
    
    for file in perseus.glob('*.json'):
        indexer.add(file)
