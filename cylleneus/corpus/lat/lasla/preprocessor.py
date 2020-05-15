import codecs
import re
from datetime import datetime
from pathlib import Path

from cylleneus.corpus.preprocessing import BasePreprocessor

from .core import AUTHOR_TAB, FILE_TAB


class Preprocessor(BasePreprocessor):
    def parse(self, file: Path):
        filename = file.name
        file_author, file_title, abbrev = filename.rstrip(".BPN").split("_")

        uids = FILE_TAB[file_author][file_title]
        if len(uids) > 1 and abbrev[-1].isdigit():
            i = int(re.search(r"(\d+)$", abbrev).group(1)) - 1
            uid = uids[i]
        else:
            uid = uids[0]
        author = AUTHOR_TAB[uid[0]]["author"]
        codes = AUTHOR_TAB[uid[0]]["code"]
        for code in codes:
            if uid[1:] in AUTHOR_TAB[uid[0]][code]:
                author_code = code
                work_code = AUTHOR_TAB[uid[0]][code][uid[1:]]["code"]
                title = AUTHOR_TAB[uid[0]][code][uid[1:]]["title"]
                meta = AUTHOR_TAB[uid[0]][code][uid[1:]]["meta"]

        urn = f"urn:cts:latinLit:{author_code}.{work_code}"
        with codecs.open(file, "r", "utf8") as f:
            doc = f.readlines()
        data = {"text": doc, "meta": meta}
        return {
            "author":       author,
            "title":        title,
            "language":     "lat",
            "urn":          urn,
            "meta":         meta,
            "form":         data,
            "lemma":        data,
            "synset":       data,
            "annotation":   data,
            "semfield":     data,
            "morphosyntax": data,
            "filename":     file.name,
            "datetime":     datetime.now(),
        }
