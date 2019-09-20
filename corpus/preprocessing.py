import codecs
import re
from abc import abstractmethod
from datetime import datetime
from pathlib import Path
import lxml.etree as et


class Preprocessor:
    @abstractmethod
    def parse(self, file: Path):
        raise NotImplementedError


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


class PerseusJSONPreprocessor(Preprocessor):
    def parse(self, file: Path):
        import json

        with codecs.open(file, 'r', 'utf8') as f:
            data = json.load(f)

        return {
            'author': data['author'].title(),
            'title': data['originalTitle'].title(),
            'meta': data['meta'].lower(),
            'urn': data['original-urn'].rsplit('.', maxsplit=1)[0] if 'original-urn' in data else "",
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


class PROIELPreprocessor(Preprocessor):
    def parse(self, file: Path):
        from corpus.proiel import AUTHOR_TAB

        with codecs.open(file, 'rb') as f:
            value = f.read()
        parser = et.XMLParser(encoding='utf-8')
        doc = et.XML(value, parser=parser)

        _author = doc.find('source').find('author').text
        _title = doc.find('source').find('title').text

        author = AUTHOR_TAB[_author]['author']
        title = AUTHOR_TAB[_author]['works'][_title]['title']
        meta = AUTHOR_TAB[_author]['works'][_title]['meta']
        urn = AUTHOR_TAB[_author]['works'][_title]['urn']
        data = {'text': doc, 'meta': meta}

        return {
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


class AGLDTPreprocessor(Preprocessor):
    def parse(self, file: Path):
        from corpus.phi5 import AUTHOR_TAB

        with codecs.open(file, 'rb') as f:
            value = f.read()
        parser = et.XMLParser(encoding='utf-8')
        doc = et.XML(value, parser=parser)

        urn = doc.get('cts')

        auth_code, work_code = urn.rsplit(':', maxsplit=1)[1].split('.')[:2]

        author = AUTHOR_TAB[auth_code]['author']
        title = AUTHOR_TAB[auth_code]['works'][work_code]['title']
        meta = AUTHOR_TAB[auth_code]['works'][work_code]['meta']

        data = {'text': doc, 'meta': meta}

        return {
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
        path = str(file.relative_to('corpus/latin_library/text')).replace('\\', '/')

        author = FILE_TAB[path]['author']
        title = FILE_TAB[path]['title']

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
            'filename': str(file.relative_to('corpus/latin_library/text')),
            'datetime': datetime.now()
        }


preprocessors = {
    'agldt': AGLDTPreprocessor,
    'lasla': LASLAPreprocessor,
    'latin_library': LatinLibraryPreprocessor,
    'proiel': PROIELPreprocessor,
    'perseus': PerseusJSONPreprocessor,
    'perseus_xml': PerseusXMLPreprocessor,
}
