import queue
import shutil
from pathlib import Path

import cylleneus.engine.index
from cylleneus.engine.writing import CLEAR
from cylleneus.settings import CORPUS_DIR
from cylleneus.utils import DEBUG_HIGH, DEBUG_MEDIUM, print_debug, slugify


class IndexingError(Exception):
    pass


def doc_for_docix(corpus, docix: int):
    toc_filename = next(corpus.index_dir.glob(f"*/*/*_{docix}_*.toc"))

    indexname = (
        "_".join(toc_filename.name.replace(".toc", "").rsplit("_", maxsplit=4)[:4])
    ).strip("_")
    path = Path(toc_filename).parent

    if cylleneus.engine.index.exists_in(path, indexname=indexname):
        ix = cylleneus.engine.index.open_dir(
            path, schema=corpus.schema, indexname=indexname
        )
        doc = ix.reader().stored_fields(0)
        return doc


def docs_for(corpus, author: str = "*", title: str = "*"):
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


class Indexer:
    def __init__(self, corpus, work, language="lat"):
        self._corpus = corpus
        self._work = work
        self._language = language
        self._index_files = []

        if work.author and work.title:
            self._path = Path(
                self.corpus.index_dir / slugify(work.author) / slugify(work.title)
            )
        else:
            self._path = None

        if self.path:
            self._index_files = Path(self.path).glob("*.toc")

    @property
    def work(self):
        return self._work

    @property
    def corpus(self):
        return self._corpus

    def exists(self):
        return cylleneus.engine.index.exists_in(self.path)

    @corpus.setter
    def corpus(self, cp):
        self._corpus = cp

    def index_for_docix(self, docix: int):
        toc_filename = next(self.path.glob(f"*_{docix}_*.toc"))

        indexname = (
            "_".join(toc_filename.name.replace(".toc", "").rsplit("_", maxsplit=4)[:4])
        ).strip("_")
        path = Path(toc_filename).parent

        if cylleneus.engine.index.exists_in(path, indexname=indexname):
            ix = cylleneus.engine.index.open_dir(
                path, schema=self.corpus.schema, indexname=indexname
            )
            return ix

    @property
    def indexes(self):
        for index in self._index_files:
            indexname = (
                "_".join(index.name.replace(".toc", "").rsplit("_", maxsplit=4)[:4])
            ).strip("_")

            if cylleneus.engine.index.exists_in(self.path, indexname=indexname):
                ix = cylleneus.engine.index.open_dir(
                    self.path, schema=self.corpus.schema, indexname=indexname
                )
                yield ix

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
        if docix is not None:
            self.corpus.manifest.pop(docix)
            self.corpus.update_manifest()

    def optimize(self):
        for ix in self.indexes:
            tocfilename, indexname = ix.optimize()
            print_debug(DEBUG_MEDIUM, f"- Optimized: {tocfilename}, {indexname}")
            for docix in ix.reader().all_doc_ixs():
                print_debug(DEBUG_HIGH, f"- Updating manifest for: {docix}")
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
        docix = self.from_file(path, destructive=True)
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
                    and doc["filename"] == kwargs["filename"]
                ):
                    existing = docix

            if existing is not None:
                if destructive:
                    self.destroy(existing)
                    print_debug(DEBUG_HIGH, f"- Docix {existing} already exists, deleting")
                else:
                    print_debug(DEBUG_HIGH, f"- Docix {existing} already exists, skipping")
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
                writer.add_document(**kwargs)
                writer.commit(optimize=optimize)
            except queue.Empty as e:
                pass

            work_manifest = {
                "author":   kwargs["author"],
                "title":    kwargs["title"],
                "filename": kwargs["filename"],
                "path":     str(self.path.relative_to(CORPUS_DIR)),
                "index":    [
                    cylleneus.engine.index.TOC._filename(
                        indexname, ix.latest_generation()
                    ),
                    writer.newsegment.make_filename(".seg"),
                ],
            }
            self.corpus.update_manifest(docix, work_manifest)
            print_debug(
                DEBUG_MEDIUM,
                f"- Indexed '{self.corpus.name}' docix {docix}: {kwargs['author']}, {kwargs['title']} ({path})"
            )
            return docix

    def from_string(
        self, content, destructive: bool = False, optimize: bool = False, **kwargs
    ):
        if content:
            parsed = self.corpus.preprocessor.parse(content)
            kwargs.update(parsed)

            # Check if docix exists
            existing = None
            for docix, doc in self.corpus.manifest.items():
                if (
                    doc["author"] == kwargs["author"]
                    and doc["title"] == kwargs["title"]
                    and doc["filename"] == kwargs["filename"]
                ):
                    existing = docix

            if existing is not None:
                if destructive:
                    self.destroy(existing)
                    print_debug(DEBUG_HIGH, f"- Docix {existing} already exists, deleting")
                else:
                    print_debug(DEBUG_HIGH, f"- Docix {existing} already exists, skipping")
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
            print_debug(
                DEBUG_MEDIUM,
                f"- Indexed '{self.corpus.name}' docix {docix}: {kwargs['author']}, {kwargs['title']} (\"{content[:24]}"
                f"...\")"
            )
            self.corpus.update_manifest(docix, work_manifest)
            return docix
