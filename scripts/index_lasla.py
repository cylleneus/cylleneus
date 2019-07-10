import codecs
import pathlib
import re

from tqdm import tqdm

import engine.index
from engine import schemas
from cylleneus.corpus.utils.lasla import FILE_TAB, AUTHOR_TAB

if __name__ == '__main__':
    lasla = pathlib.Path('../corpus/text/lasla/')
    ix = engine.index.create_in('../index/lasla/', schemas.LASLADocumentSchema())
    writer = ix.writer(limitmb=1024)

    files = lasla.glob('*.BPN')

    prev_work_code = None
    prev_author_code = None
    for docix, file in enumerate(tqdm(files, ncols=80, desc='Indexing')):
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
        data = { 'text': doc, 'meta': meta }

        writer.add_document(docix=docix,
                            author=author,
                            title=title,
                            urn=urn,
                            meta=meta,
                            form=data,
                            lemma=data,
                            synset=data,
                            annotation=data,
                            semfield=data,
                            morphosyntax=data)
        prev_work_code = work_code
        prev_author_code = author_code
    writer.commit()
