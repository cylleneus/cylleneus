from collections import namedtuple
import importlib
import pkgutil

from . import default

CorpusMeta = namedtuple(
    "CorpusMeta", ["language", "schema", "tokenizer", "preprocessor", "glob", "fetch", "repo"]
)

manifest = {
    "default": CorpusMeta(
        default.language,
        default.DocumentSchema,
        default.Tokenizer,
        default.Preprocessor,
        default.glob,
        default.fetch,
        default.repo
    )
}

for l_finder, l_name, l_is_pkg in pkgutil.walk_packages(["cylleneus/corpus"], "cylleneus.corpus."):
    if l_is_pkg:
        l_pkg = importlib.import_module(l_name)
        for c_finder, c_name, c_is_pkg in pkgutil.walk_packages(l_pkg.__path__, l_pkg.__name__ + "."):
            if c_is_pkg:
                c_pkg = importlib.import_module(c_name)
                if hasattr(c_pkg, "meta"):
                    manifest[c_name.split(".")[-1]] = c_pkg.meta
