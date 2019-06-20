import codecs
import json
import pathlib

from engine.analysis.tokenizers import CachedPerseusJSONTokenizer

if __name__=='__main__':
    perseus = pathlib.Path('../text/perseus')
    files = perseus.glob('ovid__ibis*.json')
    for file in files:
        with codecs.open(file, 'r', 'utf8') as f:
            data = json.load(f)

        divs = data['meta'].split('-')
        # content = '\n'.join([el for el in flatten(value['text'])])
        # for i, c in enumerate(content):
        #     print(f"{i:10} {c}")

        T = CachedPerseusJSONTokenizer()

        for t in T(data=data, mode='index'):
            #tags = ', '.join([f"{div.lower()}={getattr(t, div.lower())}" for div in divs])
            print(f"{t.pos} : {t.startchar}-{t.original} | {t.text}-{t.endchar}")

    # print(f"{i:8}{l:8}{t:20}{s:8}{e:8}")
    # for t in T(value):
    #     print(f"{t.pos:<8}{t.lpos:<8}{t.text:20}{t.startchar:<8}{t.endchar:<8}{t.dtitle if hasattr(t, 'dtitle') else ''} {t.etitle}")
