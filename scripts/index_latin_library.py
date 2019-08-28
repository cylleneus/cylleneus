from pathlib import Path

from corpus import Corpus, Work

if __name__ == '__main__':
    latin_library = Corpus('latin_library')
    path = Path('corpus/latin_library/text/')

    for file in path.glob('*/*.txt'):
        w = Work(corpus=latin_library)
        w.indexer.from_file(file)
