import re

# from search.proiel import CachedPROIELXmlTokenizer
from cltk.corpus.readers import get_corpus_reader

from engine.analysis.tokenizers import CachedPlainTextTokenizer

c = get_corpus_reader(language='latin', corpus_name='latin_text_latin_library')
doc = list(c.docs())[447]
doc = re.sub(r"\.,", ".", doc)
doc = re.sub(r"([\w])\.([\w])", r"\1. \2", doc)
doc = re.sub(r",([\w])", r", \1", doc)
doc = re.sub(r"(?<=\w)\.\.", r" . .", doc)
doc = re.sub(r"([.,;:])([.,;:])", r"\1 \2", doc)
doc = re.sub(r"[\t\r\n ]+", " ", doc)
doc = re.sub(r'\.\"', '\"\.', doc)
doc = re.sub(r' ,', ',', doc)
doc = re.sub(r'\[ \d+ \] ', '', doc)
doc = re.sub(r' \[,', '[,', doc)
doc = re.sub(r'\]\.', '.]', doc)


for i, c in enumerate(doc):
    print(f"{i:10} {c}")
T = CachedPlainTextTokenizer()

# T = CachedPROIELXmlTokenizer()
# with open('proiel-treebank/cic-off.xml', 'rb') as f:
#     doc = f.read()

for t in T(doc):
    print(f"{t.startchar}-{t.original} | {t.text}-{t.endchar}")
