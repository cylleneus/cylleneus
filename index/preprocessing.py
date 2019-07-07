import codecs
from pathlib import Path
import re
from abc import abstractmethod

class Preprocessor:
    @abstractmethod
    def parse(self, file: Path):
        """ Must be overriden in child class """
        pass

class DefaultPreprocessor(Preprocessor):
    def parse(self, file: Path):
        with codecs.open(file, 'r', 'utf8') as fp:
            data = fp.read()
        return {
            'form': data,
            'lemma': data,
            'synset': data,
            'annotation': data,
            'semfield': data
        }

class LASLAPreprocessor(Preprocessor):
    def parse(self, file: Path):
        from corpus.utils.lasla import FILE_TAB, AUTHOR_TAB

        filename = file.name
        file_author, file_title, abbrev = filename.rstrip('.BPN').split('_')

        uids = FILE_TAB[file_author][file_title]
        if len(uids) > 1 and abbrev[-1].isdigit():
            i = int(re.search(r"(\d+)$", abbrev).group(1)) - 1
            uid = uids[i]
        else:
            uid = uids[0]
        author = AUTHOR_TAB[uid[0]]['author']
        codes = AUTHOR_TAB[uid[0]]['code']
        for code in codes:
            if uid[1:] in AUTHOR_TAB[uid[0]][code]:
                author_code = code
                work_code = AUTHOR_TAB[uid[0]][code][uid[1:]]['code']
                title = AUTHOR_TAB[uid[0]][code][uid[1:]]['title']
                meta = AUTHOR_TAB[uid[0]][code][uid[1:]]['meta']

        urn = f'urn:cts:latinLit:{author_code}.{work_code}'
        with codecs.open(file, 'r', 'utf8') as f:
            doc = f.readlines()
        data = {
            'text': doc,
            'meta': meta
        }
        return {
            'author': author,
            'title': title,
            'urn': urn,
            'meta': meta,
            'form': data,
            'lemma': data,
            'synset': data,
            'annotation': data,
            'semfield': data,
            'morphosyntax': data
        }


preprocessors = {
    'plain_text': None,
    'lasla': LASLAPreprocessor,
    'latin_library': None,
    'proiel': None,
    'phi5': None,
    'perseus': None,
}
