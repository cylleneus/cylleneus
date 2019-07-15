import pathlib
from index import Indexer
from corpus import Corpus
import config

if __name__ == '__main__':
    latin_library = pathlib.Path(config.ROOT_DIR / '/index/texts/latin_library/')
    indexer = Indexer(Corpus('latin_library'))

    for file in latin_library.glob('*.txt'):
        author, title, _ = file.name.split('.')
    indexer.add(file, author=author, title=title)
