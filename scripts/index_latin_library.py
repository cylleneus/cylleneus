import pathlib

from corpus import Corpus, Indexer

if __name__ == '__main__':
    latin_library = pathlib.Path('corpus/latin_library/text/')
    indexer = Indexer(Corpus('latin_library'))
    indexer.destroy()

    for file in latin_library.glob('*/*.txt'):
        indexer.add(file)
    indexer.optimize()
