import codecs
from datetime import datetime
from pathlib import Path
from collections import defaultdict

from cylleneus.corpus.preprocessing import BasePreprocessor
from .core import lemma_id, lemma_morpho

class Preprocessor(BasePreprocessor):
    def parse(self, file: Path):
        filename = file.name
        author = "-"
        title = filename.split(".conllu")[0].split("-")[0]

        urn = filename.split(".conllu")[0]
        meta = "book-hymn-verse-pada"

        with codecs.open(file, "r", "utf8") as fp:
            doc = fp.readlines()
        
        # Gather dependency relations
        positions_lemmas = defaultdict(lambda: defaultdict(list))
        relations_heads = defaultdict(lambda: defaultdict(list))
        current_sent_id = None
        for line in doc:
            line = line.strip()
            if line:
                if line.startswith("#"):
                    try:
                        label, value = line.split("=", maxsplit=1)
                    except ValueError:
                        continue
                    label = label.strip('#').strip()
                    value = value.strip()
                    
                    if label == "sent_id":
                        current_sent_id = value
                else:
                    (
                        ID,
                        _,
                        LEMMA,
                        _,
                        _,
                        _,
                        _,
                        _,
                        _,
                        _,  #
                        LEMMA_ID,
                        _,  # annotator
                        _,
                        _,
                        _,
                        _,
                    ) = line.split("\t")
                    
                    try:
                        morphos = lemma_morpho[LEMMA_ID]
                        for morpho in morphos.split():
                            positions_lemmas[current_sent_id][int(ID)].append((LEMMA, lemma_id[LEMMA][morpho], morpho))
                    except:
                        pass

        current_sent_id = None
        for line in doc:
            line = line.strip()
            if line:
                if line.startswith("#"):
                    try:
                        label, value = line.split("=", maxsplit=1)
                    except ValueError:
                        continue
                    label = label.strip('#').strip()
                    value = value.strip()
                    
                    if label == "sent_id":
                        current_sent_id = value
                else:
                    (
                        ID,
                        _,
                        _,
                        _,
                        _,
                        _,
                        HEAD,
                        _,
                        _,
                        _,  #
                        _,
                        _,  # annotator
                        _,
                        _,
                        _,
                        _,
                    ) = line.split("\t")
                    
                    for lemma, uri, morpho in positions_lemmas[current_sent_id][int(HEAD)]:
                        relations_heads[current_sent_id][int(ID)].append(f"{lemma}:{uri}={morpho}")
        data = {"text": doc, "meta": meta, "deprel": relations_heads}

        return {
            "author":       author,
            "title":        title,
            "language":     "skt",
            "urn":          urn,
            "meta":         meta,
            "form":         data,
            "lemma":        data,
            "synset":       data,
            "annotation":   data,
            "semfield":     data,
            "morphosyntax": data,
            "deprel":       data,
            "filename":     file.name,
            "datetime":     datetime.now(),
        }
