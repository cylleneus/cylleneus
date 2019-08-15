import pathlib

from corpus import Corpus, Indexer

if __name__ == '__main__':
    lasla = pathlib.Path('corpus/lasla/text/')
    indexer = Indexer(Corpus('lasla'))
    indexer.destroy()

    for file in lasla.glob('*.BPN'):
        indexer.add(file)
