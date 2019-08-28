from pathlib import Path

from corpus import Corpus, Work

if __name__ == '__main__':
    perseus = Corpus('perseus')
    path = Path('corpus/perseus/text/')

    for file in path.glob('*.json'):
        w = Work(corpus=perseus)
        w.indexer.from_file(file)
