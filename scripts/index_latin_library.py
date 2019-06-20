import re

from cltk.corpus.readers import get_corpus_reader
from tqdm import tqdm

import engine.index
from engine import schemas

if __name__ == '__main__':
    # Create the index in 'index/<corpus>'
    ix = engine.index.create_in('../index/latin_library', schemas.PlainTextDocumentSchema())
    writer = ix.writer(limitmb=2048)

    # Create a list of raw-text documents
    c = get_corpus_reader(language='latin', corpus_name='latin_text_latin_library')
    corpus = list(c.docs())

    for i, doc in enumerate(tqdm(corpus, ncols=80, desc='Indexing')):
        # If the document contains the author's name, extract it
        author = ''

        # If the document contains the work's title, extract it
        title = doc.split('\r\n')[0]

        # Clean the text as much as possible
        doc = re.sub(r"\.,", ".", doc)
        doc = re.sub(r"([\w])\.([\w])", r"\1. \2", doc)
        doc = re.sub(r",([\w])", r", \1", doc)
        doc = re.sub(r"(?<=\w)\.\.", r" . .", doc)
        doc = re.sub(r"([.,;:])([.,;:])", r"\1 \2", doc)
        doc = re.sub(r"[\t\r\n ]+", " ", doc)
        doc = re.sub(r'\.\"', r'\"\.', doc)
        doc = re.sub(r' ,', ',', doc)
        doc = re.sub(r'\[ \d+ \] ', '', doc)
        doc = re.sub(r' \[,', '[,', doc)
        doc = re.sub(r'\]\.', '.]', doc)

        writer.add_document(docix=i, author=author, title=title, content=doc, form=doc, lemma=doc, synset=doc, annotation=doc, semfield=doc)
    writer.commit()
