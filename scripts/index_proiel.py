from pathlib import Path

from corpus import Corpus, Work

if __name__ == '__main__':
    proiel = Corpus('proiel')
    path = Path('../corpus/proiel/text/')

    for file in path.glob('*.xml'):
        w = Work(corpus=proiel)
        w.indexer.from_file(file)
