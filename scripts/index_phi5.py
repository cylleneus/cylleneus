import codecs
import pathlib
import re

from tqdm import tqdm

import engine.index
from cylleneus.corpus.utils.phi5 import AUTHOR_TAB
from engine import schemas

if __name__ == '__main__':
    phi5 = pathlib.Path('../corpus/text/phi5/')
    ix = engine.index.create_in('../index/phi5/', schemas.PHI5DocumentSchema())
    writer = ix.writer(limitmb=2048)

    files = phi5.glob('*.txt')

    for docix, file in enumerate(tqdm(files, ncols=80, desc='Indexing')):
        code = file.name.lstrip('LAT').rstrip('.txt')
        auth_code, work_code = code.split('-')
        auth_code = 'phi' + auth_code
        work_code = 'phi' + work_code

        with codecs.open(file, 'r', 'utf8') as f:
            doc = f.read()
            content = re.sub(r".*?\t", "", doc)
            data = { 'text': doc, 'meta': AUTHOR_TAB[auth_code]['works'][work_code]['meta'] }
        writer.add_document(docix=docix, code=code, author=AUTHOR_TAB[auth_code]['author'], title=AUTHOR_TAB[auth_code]['works'][work_code]['title'], source=AUTHOR_TAB[auth_code]['works'][work_code]['source'], meta=AUTHOR_TAB[auth_code]['works'][work_code]['meta'], content=content, form=data, lemma=data, synset=data, annotation=data, semfield=data)
    writer.commit()
