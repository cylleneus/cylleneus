import pathlib
from index import Indexer
from corpus import Corpus


if __name__ == '__main__':
    latin_library = pathlib.Path('index/texts/latin_library/')
    indexer = Indexer(Corpus('latin_library'))
    indexer.destroy()

    for file in latin_library.glob('*.txt'):
        author, title, _ = file.name.split('.')
        indexer.add(file, author=author, title=title)
