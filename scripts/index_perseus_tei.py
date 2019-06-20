import codecs
import pathlib
import re
from corpus.utils.phi5 import AUTHOR_TAB

import lxml.etree as et
from tqdm import tqdm

import engine.index
import engine.schemas

if __name__ == '__main__':
    perseus = pathlib.Path('../corpus/text/perseus-tei/data/')
    ix = engine.index.create_in('../index/perseus-tei/', engine.schemas.PerseusTEIDocumentSchema())
    writer = ix.writer(limitmb=4056)

    files = perseus.glob('*/*/*lat?.xml')

    for docix, file in enumerate(tqdm(files, ncols=80, desc='Indexing')):
        auth_code, work_code, _, _ = file.name.split('.')
        urn = 'urn:cts:latinLit:' + f"{auth_code}.{work_code}"
        author = AUTHOR_TAB[auth_code]['author']
        title = AUTHOR_TAB[auth_code]['works'][work_code]['title']
        meta = AUTHOR_TAB[auth_code]['works'][work_code]['meta']

        with codecs.open(file, 'rb') as f:
            value = f.read()
            parser = et.XMLParser(encoding='utf-8')
            doc = et.XML(value, parser=parser)
        data = { 'text': doc, 'meta': meta }
        writer.add_document(docix=docix, filename=file.name,
                            code=f"{auth_code}.{work_code}", urn=urn, author=author,
                            title=title, meta=meta, form=data, lemma=data, synset=data,
                            annotation=data, semfield=data)
    writer.commit()
