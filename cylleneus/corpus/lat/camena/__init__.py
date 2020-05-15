from .preprocessor import Preprocessor
from .schema import DocumentSchema
from .tokenizer import Tokenizer
from .core import *

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
