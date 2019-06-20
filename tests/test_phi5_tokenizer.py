import codecs
import re

from engine.analysis.tokenizers import CachedPHI5Tokenizer

if __name__=='__main__':
    file = '../text/phi5/LAT0119-002.txt'
    with codecs.open(file, 'r', 'utf8') as f:
        value = f.read()

    content = re.sub(r".*?\t", "", value)
    content = re.sub(r"_", " ", content)
    value = re.sub(r"_", " ", value)
    with codecs.open(file.split('/')[-1], 'w', 'utf8') as o:
        for i, c in enumerate(content):
            o.write(f"{i:10} {c}\n")

        T = CachedPHI5Tokenizer()
        data = { 'meta': 'fragment-verse', 'text': value}
        i = 'POS'
        l = 'IN LINE'
        t = 'TEXT'
        s = 'START'
        e = 'END'

        # for t in T(data):
        #     print(f"{t.startchar}-{t.original} | {t.text}-{t.endchar}")

        #print(f"{i:8}{l:8}{t:20}{s:8}{e:8}")
        for t in T(data):
            print(t)
            #o.write(f"{t.startchar}-{t.original} | {t.text}-{t.endchar}\n")
