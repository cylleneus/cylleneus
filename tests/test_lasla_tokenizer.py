import codecs
import pathlib
from cylleneus.corpus.utils.lasla import FILE_TAB, AUTHOR_TAB
import re
from engine.analysis.tokenizers import CachedLASLATokenizer

if __name__ == '__main__':
    lasla = pathlib.Path('../text/lasla/')
    files = lasla.glob('*Catul.BPN')

    errors = []
    for file in files:
        with codecs.open(file, 'r', 'utf8') as f:
            doc = f.readlines()

        file_author, file_title, abbrev = file.name.rstrip('.BPN').split('_')

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
                joined_code = code + '.' + AUTHOR_TAB[uid[0]][code][uid[1:]]['code']
                title = AUTHOR_TAB[uid[0]][code][uid[1:]]['title']
                meta = AUTHOR_TAB[uid[0]][code][uid[1:]]['meta']

        #     for line in doc:
        #         parsed = corpus.utils.lasla.parse_bpn(line)
        #         if not parsed:
        #             continue
        #         lemma = parsed['lemma']
        #         if lemma is None:
        #             continue
        #         ix = parsed['lemma_n']
        #         if ix == ' ':
        #             ix = '-'
        #
        #         try:
        #             morph_codes = corpus.utils.lasla.lexicon[lemma][ix]
        #         except KeyError:
        #             errors.append((lemma, ix))
        #         else:
        #             try:
        #                 for code in morph_codes:
        #                     morpho = corpus.utils.lasla.DICT_MORPH[code[0]][code[1]]
        #             except KeyError:
        #                 errors.append((lemma, ix, code))
        #             else:
        #                 pass
        # # with codecs.open('errors.json', 'w', 'utf8') as fp:
        # #     json.dump(list(set(errors)), fp)
        T = CachedLASLATokenizer()
        for t in T({"text": doc, "meta": meta}, mode='index'):
            print(t)
