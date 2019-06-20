import codecs
import json
import pathlib

from tqdm import tqdm

import engine.index
from engine import schemas

if __name__ == '__main__':
    perseus = pathlib.Path('../corpus/text/perseus/')
    ix = engine.index.create_in('../index/perseus/', schemas.PerseusJSONDocumentSchema())
    writer = ix.writer(limitmb=1024)

    files = perseus.glob('*.json')

    for docix, file in enumerate(tqdm(files, ncols=80, desc='Indexing')):
        with codecs.open(file, 'r', 'utf8') as f:
            data = json.load(f)
        filename = file.name
        writer.add_document(docix=docix,
                            filename=filename,
                            author=data['author'].title(),
                            title=data['originalTitle'].title(),
                            meta=data['meta'].lower(),
                            form=data,
                            lemma=data,
                            synset=data,
                            annotation=data,
                            semfield=data)
    writer.commit()
