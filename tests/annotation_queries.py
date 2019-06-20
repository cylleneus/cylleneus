from search import Searcher
from corpus import Corpus
import datetime

corpora = ['lasla', 'perseus', 'latin_library']
queries = {
            'verb': ":VB.",
            'noun': ":NN.",
            'adjective': ":ADJ.",
            'adverb': ":ADV.",
            'genitive': ":GEN.",
            'accusative plural': ":ACC.PL.",
            'present subjunctive': ":PRS.SBJV.",
            '2nd person singular': ":2SG.",
            'masculine plural': ":M.PL.",
            'virtus, singular': "<virtus>:SG.",
            'virtus, plural': "<virtus>:PL.",
            'virtus, ablative': "<virtus>:ABL.",
            'virtus, ablative plural': "<virtus>:PL.ABL.",
            'habeo, 3rd person plural': "<habeo>:3PL.",
            'verb, plural': ":VB.PL.",
            'habeo, subjunctive': "<habeo>:SBJV.",
            'verb, subjunctive plural': ":VB.PL.SBJV.",
            'cum + ablative': '"cum :ABL."',  # adjacency
            }
for corpus in corpora:
    c = Corpus(corpus)
    e = Searcher(c)
    print('searching in:', corpus)
    for k, v in queries.items():
        print('    ', k, end='... ')
        start = datetime.datetime.now()
        # set debug to True to see how annotation queries resolve
        results = list(e.search(v, debug=False).results)
        end = datetime.datetime.now()
        hits = len(set([hit.docnum for hit, _, _ in results]))
        matches = len(results)
        print(f"{matches} matches in {hits} docs in {end - start} secs")
