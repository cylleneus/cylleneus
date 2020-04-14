from .preprocessor import Preprocessor
from .schema import DocumentSchema
from .tokenizer import Tokenizer
from .core import *

from cylleneus.corpus.meta import CorpusMeta

meta = CorpusMeta(
    language,
    DocumentSchema,
    Tokenizer,
    Preprocessor,
    glob,
    fetch,
    repo
)
