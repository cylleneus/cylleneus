from engine.fields import *
from engine.schemas import BaseSchema
from engine.analysis.filters import CachedSynsetFilter, AnnotationFilter, SemfieldFilter

from .tokenizer import CachedTokenizer
from .filters import CachedLemmaFilter


Tokens = CachedTokenizer(chars=True)
Lemmas = CachedLemmaFilter(chars=True)
Synsets = CachedSynsetFilter()
Annotations = AnnotationFilter()
Semfields = SemfieldFilter()
