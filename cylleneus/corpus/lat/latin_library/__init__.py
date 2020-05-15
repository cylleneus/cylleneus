from .preprocessor import Preprocessor
from .schema import DocumentSchema
from .core import *

from cylleneus.corpus.meta import CorpusMeta
from cylleneus.corpus.default import Tokenizer

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
