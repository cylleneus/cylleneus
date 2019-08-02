import codecs
import re
from abc import abstractmethod
from datetime import datetime
from pathlib import Path


class Preprocessor:
    @abstractmethod
    def parse(self, file: Path):
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
            'semfield': data,
            'filename': file.name,
            'datetime': datetime.now()
        }


class LASLAPreprocessor(Preprocessor):
    def parse(self, file: Path):
        from corpus.lasla import FILE_TAB, AUTHOR_TAB

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
            'morphosyntax': data,
            'filename': file.name,
            'datetime': datetime.now()
        }


class PHI5Preprocessor(Preprocessor):
    def parse(self, file: Path):
        from corpus.phi5 import AUTHOR_TAB

        code = file.name.lstrip('LAT').rstrip('.txt')
        auth_code, work_code = code.split('-')
        auth_code = 'phi' + auth_code
        work_code = 'phi' + work_code

        with codecs.open(file, 'r', 'utf8') as f:
            doc = f.read()
            content = re.sub(r".*?\t", "", doc)
            data = {'text': doc, 'meta': AUTHOR_TAB[auth_code]['works'][work_code]['meta']}
        return {
            'code': code,
            'author': AUTHOR_TAB[auth_code]['author'],
            'title': AUTHOR_TAB[auth_code]['works'][work_code]['title'],
            'source': AUTHOR_TAB[auth_code]['works'][work_code]['source'],
            'meta': AUTHOR_TAB[auth_code]['works'][work_code]['meta'],
            'content': content,
            'form': data,
            'lemma': data,
            'synset': data,
            'annotation': data,
            'semfield': data,
            'filename': file.name,
            'datetime': datetime.now()
        }


class PerseusJSONPreprocessor(Preprocessor):
    def parse(self, file: Path):
        import json

        with codecs.open(file, 'r', 'utf8') as f:
            data = json.load(f)

        return {
            'author': data['author'].title(),
            'title': data['originalTitle'].title(),
            'meta': data['meta'].lower(),
            'form': data,
            'lemma': data,
            'synset': data,
            'annotation': data,
            'semfield': data,
            'filename': file.name,
            'datetime': datetime.now()
        }


class PerseusXMLPreprocessor(Preprocessor):
    def parse(self, file: Path):
        import lxml.etree as et
        from corpus.phi5 import AUTHOR_TAB

        auth_code, work_code, _, _ = file.name.split('.')
        urn = 'urn:cts:latinLit:' + f"{auth_code}.{work_code}"
        author = AUTHOR_TAB[auth_code]['author']
        title = AUTHOR_TAB[auth_code]['works'][work_code]['title']
        meta = AUTHOR_TAB[auth_code]['works'][work_code]['meta']

        with codecs.open(file, 'rb') as f:
            value = f.read()
        parser = et.XMLParser(encoding='utf-8')
        doc = et.XML(value, parser=parser)
        data = {'text': doc, 'meta': meta}
        return {
            'code': f"{auth_code}.{work_code}",
            'urn': urn,
            'author': author,
            'title': title,
            'meta': meta,
            'form': data,
            'lemma': data,
            'synset': data,
            'annotation': data,
            'semfield': data,
            'filename': file.name,
            'datetime': datetime.now()
        }


class PlainTextPreprocessor(Preprocessor):
    def parse(self, file: Path):
        with codecs.open(file, 'r', 'utf8') as fp:
            doc = fp.read()

        # Do some tidying up
        subs = [
            (r"\.,", "."),
            (r"([\w])\.([\w])", r"\1. \2"),
            (r",([\w])", r", \1"),
            (r"(?<=\w)\.\.", r" . ."),
            (r"([.,;:])([.,;:])", r"\1 \2"),
            (r"[\t\r\n ]+", " "),
            (r'\.\"', r'\"\.'),
            (r' ,', ','),
            (r'\[ \d+ \] ', ''),
            (r' \[,', '[,'),
            (r'\]\.', '.]')
        ]
        for pattern, repl in subs:
            doc = re.sub(pattern, repl, doc)
        return {
            'content': doc,
            'form': doc,
            'lemma': doc,
            'synset': doc,
            'annotation': doc,
            'semfield': doc,
            'filename': file.name,
            'datetime': datetime.now()
        }

class LatinLibraryPreprocessor(Preprocessor):
    def parse(self, file: Path):
        from corpus.latin_library import FILE_TAB

        author = FILE_TAB[str(file.relative_to('corpus/latin_library/text'))]['author']
        title = FILE_TAB[str(file.relative_to('corpus/latin_library/text'))]['title']

        with codecs.open(file, 'r', 'utf8') as fp:
            doc = fp.read()

        # Do some tidying up
        subs = [
            (r"\.,", "."),
            (r"([\w])\.([\w])", r"\1. \2"),
            (r",([\w])", r", \1"),
            (r"(?<=\w)\.\.", r" . ."),
            (r"([.,;:])([.,;:])", r"\1 \2"),
            (r"[\t\r\n ]+", " "),
            (r'\.\"', r'\"\.'),
            (r' ,', ','),
            (r'\[ \d+ \] ', ''),
            (r' \[,', '[,'),
            (r'\]\.', '.]')
        ]
        for pattern, repl in subs:
            doc = re.sub(pattern, repl, doc)
        return {
            'author': author,
            'title': title,
            'content': doc,
            'form': doc,
            'lemma': doc,
            'synset': doc,
            'annotation': doc,
            'semfield': doc,
            'filename': file.name,
            'datetime': datetime.now()
        }


preprocessors = {
    'plain_text': PlainTextPreprocessor,
    'lasla': LASLAPreprocessor,
    'latin_library': LatinLibraryPreprocessor,
    'proiel': None,
    'phi5': PHI5Preprocessor,
    'perseus': PerseusJSONPreprocessor,
    'perseus-tei': PerseusXMLPreprocessor,
    'default': DefaultPreprocessor,
}
