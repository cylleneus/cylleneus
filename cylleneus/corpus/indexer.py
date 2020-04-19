import codecs
import queue
import shutil
from pathlib import Path

import cylleneus.engine.index
from cylleneus.engine.writing import CLEAR
from cylleneus.utils import DEBUG_HIGH, DEBUG_MEDIUM, print_debug, slugify
from cylleneus.settings import CORPUS_DIR


class IndexingError(Exception):
    pass


class Indexer:
    @classmethod
    def docs_for(cls, corpus, author: str = "*", title: str = "*"):
        paths = corpus.index_dir.glob(f"{slugify(author)}/{slugify(title)}")
        for path in paths:
            indexes = Path(path).glob("*.toc")
            for index in indexes:
                indexname = (
                    "_".join(index.name.replace(".toc", "").rsplit("_", maxsplit=4)[:4])
                ).strip("_")
                if cylleneus.engine.index.exists_in(path, indexname=indexname):
                    ix = cylleneus.engine.index.open_dir(
                        path, schema=corpus.schema, indexname=indexname
                    )
                    yield from ix.reader().iter_docs()

    def __init__(self, corpus, work, language="lat"):
        self._corpus = corpus
        self._work = work
        self._language = language
        self._indexes = []

        if work.author and work.title:
            self._path = Path(
                self.corpus.index_dir / slugify(work.author) / slugify(work.title)
            )
        else:
            self._path = None

        if self.path:
            indexes = Path(self.path).glob("*.toc")

            for index in indexes:
                indexname = (
                    "_".join(index.name.replace(".toc", "").rsplit("_", maxsplit=4)[:4])
                ).strip("_")

                if cylleneus.engine.index.exists_in(self.path, indexname=indexname):
                    ix = cylleneus.engine.index.open_dir(
                        self.path, schema=corpus.schema, indexname=indexname
                    )
                    self._indexes.append(ix)

    @property
    def work(self):
        return self._work

    @property
    def corpus(self):
        return self._corpus

    @corpus.setter
    def corpus(self, cp):
        self._corpus = cp

    @property
    def indexes(self):
        return self._indexes

    @indexes.setter
    def indexes(self, ixs):
        self._indexes = ixs

    @property
    def path(self):
        if self._path:
            return Path(self._path)

    @path.setter
    def path(self, p: Path):
        self._path = p

    def iter_docs(self):
        for ix in self.indexes:
            yield from ix.reader().iter_docs()

    def clear(self):
        for ix in self.indexes:
            with ix.writer() as writer:
                writer.commit(mergetype=CLEAR)

    def destroy(self, docix: int = None):
        if self.path and self.path.exists():
            shutil.rmtree(self.path)
            self._indexes = []
        if docix:
            self.corpus.manifest.pop(docix)

    def optimize(self):
        for ix in self.indexes:
            tocfilename, indexname = ix.optimize()
            print_debug(
                DEBUG_MEDIUM,
                f"Optimized: [{tocfilename}] {indexname}"
            )
            for docix in ix.reader().all_doc_ixs():
                manifest = self.corpus.manifest[str(docix)]
                manifest["index"] = [tocfilename, indexname]
                self.corpus.update_manifest(str(docix), manifest)

    def create(self, indexname: str = None):
        if not self.path.exists():
            self.path.mkdir(parents=True)
        cylleneus.engine.index.create_in(
            self.path, schema=self.corpus.schema, indexname=indexname
        )

    def open(self, indexname: str):
        if not cylleneus.engine.index.exists_in(self.path, indexname=indexname):
            self.create(indexname=indexname)
        ix = cylleneus.engine.index.open_dir(
            self.path, schema=self.corpus.schema, indexname=indexname
        )
        return ix

    def update(self, path: Path):
        if self.path and self.path.exists():
            self.destroy()
        docix = self.from_file(path)
        return docix

    def from_file(self, path: Path, destructive: bool = False, optimize: bool = False):
        if path.exists():

            kwargs = self.corpus.preprocessor.parse(path)
            if "author" not in kwargs and self.work.author:
                kwargs["author"] = self.work.author
            if "title" not in kwargs and self.work.title:
                kwargs["title"] = self.work.title
            kwargs["corpus"] = self.corpus.name

            # Check if docix exists
            existing = None
            for docix, doc in self.corpus.manifest.items():
                if (
                    doc["author"] == kwargs["author"]
                    and doc["title"] == kwargs["title"]
                    and doc["filename"] == path.name
                ):
                    existing = docix

            if existing is not None:
                if destructive:
                    self.destroy(existing)
                else:
                    return existing

            docix = self.corpus.doc_count_all
            kwargs["docix"] = docix

            self.path = Path(
                self.corpus.index_dir
                / slugify(kwargs["author"])
                / slugify(kwargs["title"])
            )
            indexname = f"{self.corpus.name}_{slugify(kwargs['author'])}_{slugify(kwargs['title'])}_{docix}"
            ix = self.open(indexname=indexname)

            writer = ix.writer(limitmb=4096, procs=1, multisegment=True)
            try:
                print_debug(
                    DEBUG_MEDIUM,
                    "Add document: {}, {} [{}] to '{}' [{}]".format(
                        kwargs["author"], kwargs["title"], path, self.corpus.name, docix
                    ),
                )
                writer.add_document(**kwargs)
                writer.commit(optimize=optimize)
            except queue.Empty as e:
                pass

            work_manifest = {
                "author":   kwargs["author"],
                "title":    kwargs["title"],
                "filename": str(path.name),
                "path":     str(self.path.relative_to(CORPUS_DIR)),
                "index":    [
                    cylleneus.engine.index.TOC._filename(
                        indexname, ix.latest_generation()
                    ),
                    writer.newsegment.make_filename(".seg"),
                ],
            }
            self.corpus.update_manifest(docix, work_manifest)
            return docix

    def from_string(
        self, content, destructive: bool = False, optimize: bool = False, **kwargs
    ):
        if content:
            parsed = self.corpus.preprocessor.parse(content)
            kwargs.update(parsed)

            if destructive:
                self.destroy()

            for docix, doc in self.corpus.manifest.items():
                if (
                    doc["author"] == kwargs["author"]
                    and doc["title"] == kwargs["title"]
                ):
                    return docix
            else:
                docix = self.corpus.doc_count_all
                kwargs["docix"] = docix

                self.path = Path(
                    self.corpus.index_dir
                    / slugify(kwargs["author"])
                    / slugify(kwargs["title"])
                )
                indexname = f"{self.corpus.name}_{slugify(kwargs['author'])}_{slugify(kwargs['title'])}_{docix}"
                ix = self.open(indexname=indexname)

                writer = ix.writer(limitmb=4096, procs=1, multisegment=True)
                try:
                    print_debug(
                        DEBUG_MEDIUM,
                        "Add document: {}, {} to '{}' [{}]".format(
                            kwargs["author"], kwargs["title"], self.corpus.name, docix
                        ),
                    )
                    writer.add_document(**kwargs)
                    writer.commit(optimize=optimize)
                except queue.Empty as e:
                    pass
                work_manifest = {
                    "author":   kwargs["author"],
                    "title":    kwargs["title"],
                    "filename": None,
                    "path":     str(self.path.relative_to(CORPUS_DIR)),
                    "index":    [
                        cylleneus.engine.index.TOC._filename(
                            indexname, ix.latest_generation()
                        ),
                        writer.newsegment.make_filename(".seg"),
                    ],
                }
                self.corpus.update_manifest(docix, work_manifest)
                return docix
