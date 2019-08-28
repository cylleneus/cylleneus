from pathlib import Path

from corpus import Corpus, Work

if __name__ == '__main__':
    lasla = Corpus('lasla')
    path = Path('corpus/lasla/text/')

    for file in path.glob('*.BPN'):
        w = Work(corpus=lasla)
        w.indexer.from_file(file)
