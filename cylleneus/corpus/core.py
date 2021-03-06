import codecs
from collections import defaultdict
import json
import shutil
import sys
from pathlib import Path

import requests
from git import RemoteProgress, Repo
import safer

from cylleneus import settings
import cylleneus.engine.index
from cylleneus.engine.fields import Schema
from cylleneus.engine.searching import CylleneusHit, CylleneusSearcher
from cylleneus.utils import slugify
from . import indexer
from .meta import manifest
from enum import IntEnum


class DefaultProgressPrinter:
    def __init__(self, max_count, default_message="", out=sys.stderr):
        self.max_count = max_count
        self.default_message = default_message
        self.out = out

    def __del__(self):
        self.out.write("\n")

    def update(self, cur_count, max_count=None, message=None):
        if not max_count:
            max_count = self.max_count
        if cur_count > self.max_count:
            cur_count = self.max_count
        if self.out:
            percentage = "%.0f" % (100 * cur_count / (max_count or 100.0))
            if not message:
                message = self.default_message
            self.out.write(f"\r[{percentage:>3}%] {message}")
            self.out.flush()


class ProgressPrinter(RemoteProgress):
    def __init__(self, default_message="", out=sys.stdout):
        super().__init__()
        self.default_message = default_message
        self.out = out

    def update(self, op_code, cur_count, max_count=None, message=""):
        if self.out:
            percentage = "%.0f" % (100 * cur_count / (max_count or 100.0))
            if not message:
                message = self.default_message
            self.out.write(f"\r[{percentage:>3}%] {message}")


class Corpus:
    def __init__(self, name: str):
        self._name = name

        self._meta = manifest.get(name, manifest["default"])
        self._language = self._meta.language
        self._schema = self._meta.schema()
        self._tokenizer = self._meta.tokenizer()
        self._preprocessor = self._meta.preprocessor(self)
        self._glob = self._meta.glob
        self._fetch = self._meta.fetch
        manifest_file = self.path / Path("manifest.json")
        if manifest_file.exists():
            with codecs.open(manifest_file, "r", "utf8") as fp:
                self._manifest = json.load(fp)
        else:
            self._manifest = {}
        self._remote_manifest = None

    @property
    def name(self):
        return self._name

    @property
    def meta(self):
        return self._meta

    @property
    def manifest(self):
        return self._manifest

    @manifest.setter
    def manifest(self, manifest):
        self._manifest = manifest

    def update_manifest(self, docix=None, work_manifest=None):
        if docix is not None and work_manifest:
            self.manifest[str(docix)] = work_manifest
        manifest_file = self.path / Path("manifest.json")
        if not self.path.exists():
            self.path.mkdir(parents=True, exist_ok=True)
        with safer.open(
            manifest_file, mode="w", encoding="utf8", temp_file=False
        ) as fp:
            json.dump(self.manifest, fp, ensure_ascii=False)

    @property
    def remote_manifest(self):
        if (
            self._remote_manifest is None
            and self.meta.repo["location"] == "remote"
        ):
            url = self.meta.repo["raw"] + "manifest.json"
            result = requests.get(url)
            if result:
                self._remote_manifest = json.loads(result.content)
        return self._remote_manifest

    @remote_manifest.setter
    def remote_manifest(self, manifest):
        self._remote_manifest = manifest

    @property
    def language(self):
        return self._language

    @property
    def preprocessor(self):
        return self._preprocessor

    @preprocessor.setter
    def preprocessor(self, p):
        self._preprocessor = p

    @property
    def schema(self):
        return self._schema

    @schema.setter
    def schema(self, s: Schema):
        self._schema = s

    @property
    def glob(self):
        return self._glob

    @glob.setter
    def glob(self, g):
        self._glob = g

    def optimize(self):
        for ixr in self.indexers:
            ixr.optimize()

    def verify_by_docix(self, docix, dry_run: bool = True):
        class VerificationResult(IntEnum):
            PASSED = 0
            FIXED = 1
            ADDED = 2
            ORPHANS = 3
            MISSING = 4

        docix = int(docix)
        work = self.work_by_docix(docix)

        if work is None:
            return VerificationResult.MISSING, (docix, None, None, None, None)

        try:
            passed = (
                self.manifest[str(docix)]["author"] == work.author
                and self.manifest[str(docix)]["title"] == work.title
                and self.manifest[str(docix)]["filename"] == work.filename[0][1]
                and (
                    work.indexer.path
                    / Path(self.manifest[str(docix)]["index"][0])
                ).exists()
                and (
                    work.indexer.path
                    / Path(self.manifest[str(docix)]["index"][1])
                ).exists()
            )
        except KeyError:
            ix = work.indexer.index_for_docix(docix)
            meta = {
                "author":   work.author,
                "title":    work.title,
                "filename": work.filename[0][1],
                "path":     (
                    (
                        Path(self.index_dir)
                        / Path(slugify(work.author))
                        / Path(slugify(work.title))
                    )
                        .relative_to(Path(settings.CORPUS_DIR))
                        .as_posix()
                ),
                "index":    [
                    cylleneus.engine.index.TOC._filename(
                        ix.indexname, ix.latest_generation()
                    ),
                    ix.reader().segment().make_filename(".seg"),
                ],
            }
            if not dry_run:
                self.update_manifest(str(docix), meta)
            return (
                VerificationResult.ADDED,
                (docix, work.author, work.title, work.filename[0][1], None),
            )
        else:
            indexname = work.indexer.index_for_docix(docix).indexname

            storage = cylleneus.engine.filedb.filestore.FileStorage(
                work.indexer.path
            )
            tocfiles = list(self.index_dir.glob(f"*/*/_{indexname}_*.toc"))
            latest_toc = sorted(tocfiles)[-1] if len(tocfiles) > 1 else tocfiles[0]
            gen = latest_toc.name.rsplit("_", maxsplit=1)[1].replace(
                ".toc", ""
            )
            TOC = cylleneus.engine.index.TOC.read(
                storage, indexname, gen=int(gen)
            )
            segments = [
                segment.segment_id() + ".seg" for segment in TOC.segments
            ]
            segfiles = list(self.index_dir.glob(f"*/*/{indexname}_*.seg"))

            extraneous = []
            for fp in tocfiles:
                if fp.name != latest_toc.name:
                    extraneous.append(fp)
            for fp in segfiles:
                if fp.name not in segments:
                    extraneous.append(fp)

            if extraneous:
                for fp in extraneous:
                    if not dry_run:
                        fp.unlink()
                return (
                    VerificationResult.ORPHANS,
                    (
                        docix,
                        work.author,
                        work.title,
                        work.filename[0][1],
                        ", ".join([f"{fp.name}" for fp in extraneous]),
                    ),
                )
            else:
                if passed and work.searchable:
                    return (
                        VerificationResult.PASSED,
                        (
                            docix,
                            work.author,
                            work.title,
                            work.filename[0][1],
                            None,
                        ),
                    )
                else:
                    ix = work.indexer.index_for_docix(docix)

                    meta = {
                        "author":   work.author,
                        "title":    work.title,
                        "filename": work.filename[0][1],
                        "path":     (
                            (
                                Path(self.index_dir)
                                / Path(slugify(work.author))
                                / Path(slugify(work.title))
                            )
                                .relative_to(Path(settings.CORPUS_DIR))
                                .as_posix()
                        ),
                        "index":    [
                            cylleneus.engine.index.TOC._filename(
                                ix.indexname, ix.latest_generation(),
                            ),
                            ix.reader().segment().make_filename(".seg"),
                        ],
                    }
                    if not dry_run:
                        self.update_manifest(str(docix), meta)
                    return (
                        VerificationResult.FIXED,
                        (
                            docix,
                            work.author,
                            work.title,
                            work.filename[0][1],
                            None,
                        ),
                    )

    @property
    def searchable(self):
        return self.schema and any(work.searchable for work in self.works)

    @property
    def works(self):
        for path in self.index_dir.glob("*/*"):
            yield Work(self, author=path.parts[-2], title=path.name)

    def works_for(self, author: str = None, title: str = None):
        for path in self.index_dir.glob(
            f'{slugify(author) if author else "*"}/{slugify(title) if title else "*"}'
        ):
            yield Work(self, author=path.parts[-2], title=path.name)

    def work_by_docix(self, docix: int):
        doc = indexer.doc_for_docix(self, docix)
        if doc is not None:
            return Work(self, doc=doc)

    def destroy(self):
        for ixr in self.indexers:
            ixr.destroy()
        mfest = self.path / Path("manifest.json")
        if mfest.exists():
            mfest.unlink()

    def delete_by(self, **kwargs):
        for reader in self.readers:
            with CylleneusSearcher(reader) as searcher:
                results = searcher.document_numbers(**kwargs)
                if results:
                    for docix in results:
                        self.delete_by_ix(docix)

    def delete_by_ix(self, docix: int):
        for ixr in self.indexers:
            for ix in ixr.indexes:
                if docix in ix.reader().all_doc_ixs():
                    ixr.destroy()

    @property
    def doc_count_all(self):
        return len(list(self.index_dir.glob("*/*/*.toc")))

    def all_doc_ixs(self):
        docixs = []
        for ixr in self.indexers:
            for ix in ixr.indexes:
                docixs += ix.reader().all_doc_ixs()
        return docixs

    def clear(self):
        for ixr in self.indexers:
            ixr.clear()

    def update(self, docix: int, path: Path):
        ixr = self.indexer_for_docix(docix)
        return ixr.update(path)

    def update_by(self, author: str, title: str, path: Path):
        ixr = list(self.indexers_for(author, title))[0]
        return ixr.update(path)

    @property
    def index_dir(self):
        return Path(self.path / "index")

    @property
    def text_dir(self):
        return Path(self.path / "text")

    def iter_docs(self):
        for reader in self.readers:
            yield from reader.iter_docs()

    @property
    def indexers(self):
        for work in self.works:
            yield work.indexer

    def indexers_for(self, author: str = None, title: str = None):
        ixrs = (work.indexer for work in self.works_for(author, title))
        yield from ixrs

    def indexer_for_docix(self, docix: int):
        doc = indexer.doc_for_docix(self, docix)
        return Work(corpus=self, doc=doc).indexer

    @property
    def readers(self):
        for ixr in self.indexers:
            if ixr.indexes:
                for ix in ixr.indexes:
                    yield ix.reader()

    def readers_for(self, author: str = "*", title: str = "*"):
        for ixr in self.indexers_for(author, title):
            for ix in ixr.indexes:
                yield ix.reader()

    def reader_for_docix(self, docix: int):
        for reader in self.readers:
            ids = list(reader.all_doc_ixs())
            if docix in ids:
                return reader

    @property
    def path(self):
        return (
            Path(settings.CORPUS_DIR) / Path(self.language) / Path(self.name)
        )

    def fetch(self, hit, meta, fragment):
        work = Work(corpus=self, doc=hit)
        urn, reference, text = work.fetch(work, meta, fragment)
        return self.name, work.author, work.title, urn, reference, text

    def download_by(self, author: str = None, title: str = None):
        if self.meta.repo["location"] != "remote":
            return
        remote_manifest = self.remote_manifest
        if author:
            manifest_by_author = defaultdict(lambda: defaultdict(list))
            for docix, meta in remote_manifest.items():
                manifest_by_author[meta["author"]][meta["title"]].append(
                    (docix, meta)
                )
            if title:
                docs = manifest_by_author[author][title]
            else:
                docs = [author[work] for work in manifest_by_author[author]]
        else:
            if title:
                manifest_by_title = defaultdict(list)
                for docix, meta in remote_manifest.items():
                    manifest_by_title[meta["title"]].append((docix, meta))
                docs = manifest_by_title[title]
            else:
                docs = []
        for docix, meta in docs:
            self.download_by_docix(docix, meta)

    def download_by_docix(self, docix, meta=None):
        if self.meta.repo["location"] != "remote":
            return
        remote_manifest = self.remote_manifest if not meta else {docix: meta}
        if remote_manifest and str(docix) in remote_manifest:
            manifest = remote_manifest[str(docix)]

            files = manifest["index"]
            for i, file in enumerate(files):
                remote_path = (
                    Path(manifest["path"])
                        .as_posix()
                        .split("/", maxsplit=2)[-1]
                )
                local_path = (
                    Path(settings.CORPUS_DIR)
                    / Path(manifest["path"]).as_posix()
                )

                if not local_path.exists():
                    local_path.mkdir(parents=True, exist_ok=True)

                url = (
                    self.meta.repo["raw"]
                    + (remote_path / Path(file)).as_posix()
                )
                with requests.get(url, stream=True) as r:
                    r.raise_for_status()
                    with safer.open(local_path / Path(file), "wb") as fp:
                        max_count = int(r.headers["Content-Length"])
                        progress = DefaultProgressPrinter(
                            max_count=max_count,
                            default_message=f"({i + 1} / 3) index/{file}",
                        )
                        cur_count = 0
                        for chunk in r.iter_content(chunk_size=10 * 1024):
                            if chunk:  # filter out keep-alive new chunks
                                fp.write(chunk)
                                cur_count += len(chunk)
                                progress.update(cur_count)

            filename = manifest["filename"]
            text_url = (
                self.meta.repo["raw"]
                + (Path("/text") / Path(filename)).as_posix()
            )
            file_path = self.text_dir / Path(filename)
            if not file_path.parent.exists():
                file_path.parent.mkdir(parents=True, exist_ok=True)
            with requests.get(text_url, stream=True) as r:
                try:
                    r.raise_for_status()
                except requests.exceptions.HTTPError as e:
                    pass
                else:
                    with safer.open(file_path, "wb") as fp:
                        max_count = int(r.headers["Content-Length"])
                        progress = DefaultProgressPrinter(
                            max_count=max_count,
                            default_message=f"(3 / 3) text/{filename}",
                        )
                        cur_count = 0
                        for chunk in r.iter_content(chunk_size=None):
                            if chunk:  # filter out keep-alive new chunks
                                fp.write(chunk)
                                cur_count += len(chunk)
                                progress.update(cur_count)
            self.update_manifest(docix, manifest)

    def download(self, branch: str = "master", destructive=False):
        if self.meta.repo["location"] != "remote":
            return
        git_uri = self.meta.repo["origin"]

        repo = None
        if not self.path.exists():
            self.path.mkdir(exist_ok=True, parents=True)
            try:
                repo = Repo.clone_from(
                    git_uri,
                    self.path,
                    branch=branch,
                    depth=1,
                    progress=ProgressPrinter(
                        default_message=f"'{self.name}', origin/{branch}: {self.meta.repo['origin']}"
                    ),
                )
            except Exception as e:
                raise e
        else:
            if destructive:
                shutil.rmtree(self.path)
                self.path.mkdir(exist_ok=True, parents=True)
                try:
                    repo = Repo.clone_from(
                        git_uri,
                        self.path,
                        branch=branch,
                        depth=1,
                        progress=ProgressPrinter(
                            default_message=f"'{self.name}', origin/{branch}: {self.meta.repo['origin']}"
                        ),
                    )
                except Exception as e:
                    raise e
            else:
                try:
                    repo = Repo(self.path)
                    if not repo.bare:
                        git_origin = repo.remotes.origin
                        git_origin.pull()
                except Exception as e:
                    raise e
        manifest_file = self.path / Path("manifest.json")
        if manifest_file.exists():
            with codecs.open(manifest_file, "r", "utf8") as fp:
                self._manifest = json.load(fp)
        return repo

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return (
            self.name == other.name
            and self.schema == other.schema
            and self.path == other.path
        )


class Work:
    def __init__(
        self,
        corpus: Corpus,
        author: str = None,
        title: str = None,
        doc: CylleneusHit = None,
        language: str = None,
    ):
        self._corpus = corpus
        if doc:
            self._doc = [
                doc,
            ]
            self._author = doc["author"] if "author" in doc else None
            self._title = doc["title"] if "title" in doc else None
            self._docix = [doc["docix"], ] if "docix" in doc else None
            self._urn = [(doc["docix"], doc["urn"]), ] if "urn" in doc else None
            self._filename = (
                [(doc["docix"], doc["filename"]), ]
                if "filename" in doc
                else None
            )
            self._timestamp = (
                [(doc["docix"], doc["datetime"]), ]
                if "datetime" in doc
                else None
            )
            self._language = doc["language"] if "language" in doc else None
        else:
            self.__author = author
            self.__title = title
            self._doc = []
            self._docix = []
            self._author = (
                self._title
            ) = self._urn = self._filename = self._timestamp = None
        self._indexer = indexer.Indexer(corpus, self)
        self.fetch = self.corpus._fetch
        self._language = language

    @property
    def searchable(self):
        return self.indexer.exists()

    @property
    def language(self):
        return self._language

    @property
    def indexer(self):
        return self._indexer

    @property
    def indexes(self):
        return self.indexer.indexes

    @property
    def author(self):
        if not self._author and len(self.doc) != 0:
            self._author = self.doc[0].get("author", None)
        return self._author

    @property
    def title(self):
        if not self._title and len(self.doc) != 0:
            self._title = self.doc[0].get("title", None)
        return self._title

    def delete(self):
        self.indexer.destroy()

    @property
    def corpus(self):
        return self._corpus

    @property
    def docix(self):
        if not self._docix and len(self.doc) != 0:
            self._docix = [doc.get("docix", None) for doc in self.doc]
        return self._docix

    @property
    def doc(self):
        if len(self._doc) == 0:
            self._doc = [
                doc[1]
                for doc in indexer.docs_for(
                    self.corpus, self.__author, self.__title
                )
            ]
        return self._doc

    @property
    def meta(self):
        if self.doc and "meta" in self.doc[0]:
            return self.doc[0]["meta"]

    @property
    def divs(self):
        return [d.lower() for d in self.meta.split("-")]

    @property
    def timestamp(self):
        if not self._timestamp and len(self.doc) != 0:
            self._timestamp = [
                (doc.get("docix", None), doc.get("docix", None))
                for doc in self.doc
            ]
        return self._timestamp

    @property
    def urn(self):
        if not self._urn and len(self.doc) != 0:
            self._urn = [
                (doc.get("docix", None), doc.get("urn", None))
                for doc in self.doc
            ]
        return self._urn

    @property
    def filename(self):
        if not self._filename and len(self.doc) != 0:
            self._filename = [
                (doc.get("docix", None), doc.get("filename", None))
                for doc in self.doc
            ]
        return self._filename

    def __str__(self):
        return f"{self.author}, {self.title} [{self.corpus.name}]"

    def __repr__(self):
        return f"Work(corpus={self.corpus}, docix={self.docix})"

    def __eq__(self, other):
        return self.docix == other.docix and self.corpus == other.corpus
