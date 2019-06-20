from search import Searcher
from corpus.core import Corpus
import datetime

corpora = ['lasla', 'perseus', 'latin_library']
queries = { 'form': "'ius'",
            'annotation': ":ACC.PL.",
            'lemma': "<virtus>",
            'lemma with annotation': "<animus>:PL.ABL.",
            'gloss (en)': "[en?war]",
            'gloss (it)': "[it?guerra]",
            'gloss (es)': "[es?guerra]",
            'gloss (fr)': "[fr?guerre]",
            'gloss with annotation': "[en?courage]:GEN.SG.",
            'semfield': "{611}",
            # 'semfield with annotation': "{611}:SG.ACC.",  # slow
            'form + lemma': '"cum <virtus>"',
            'form + lemma with annotation': '"cum <virtus>:SG."',
            'form + lemma with disqualifying annotation': '"cum <virtus>:PL."',
            'form + annotation': "'milites' :VB.",
            'annotation + form': ":VB. 'milites'",
            'annotation + lemma': ":VB. <miles>",
            'lexical relation (lemma)': "</=bellum>",
            'semantic relation (gloss)': "[!=en?love]",
            'semantic relation (synset)': "[@=n#04478900]",
            }
for corpus in corpora:
    c = Corpus(corpus)
    e = Searcher(c)
    print(f"Searching in: '{corpus}'")
    for k, v in queries.items():
        print('    ', k, end='... ')
        start = datetime.datetime.now()
        results = list(e.search(v).results)
        end = datetime.datetime.now()
        hits = len(set([hit.docnum for hit, _, _ in results]))
        matches = len(results)
        print(f"{matches} matches in {hits} docs in {end - start} secs")
