from pathlib import Path

from corpus import Corpus, Work

if __name__ == '__main__':
    agldt = Corpus('agldt')
    path = Path('../corpus/agldt/text/')

    for file in path.glob('*.txt'):
        w = Work(corpus=agldt)
        w.indexer.from_file(file)
