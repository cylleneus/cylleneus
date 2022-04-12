from .core import *
from .preprocessor import Preprocessor
from .schema import DocumentSchema
from .tokenizer import CachedTokenizer as Tokenizer

from cylleneus.corpus.meta import CorpusMeta

# Manifest information
meta = CorpusMeta(
    description,
    language,
    DocumentSchema,
    Tokenizer,
    Preprocessor,
    glob,
    fetch,
    repo,
)
