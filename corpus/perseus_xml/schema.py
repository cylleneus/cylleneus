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


class DocumentSchema(BaseSchema):
    urn = STORED()
    meta = STORED()
    form = FORM(analyzer=Tokens, vector=True)
    lemma = LEMMA(analyzer=Tokens | Lemmas, vector=True)
    annotation = ANNOTATION(analyzer=Tokens | Lemmas | Annotations, vector=True)
    synset = SYNSET(analyzer=Tokens | Lemmas | Synsets, vector=True)
    semfield = SEMFIELD(analyzer=Tokens | Lemmas | Synsets | Semfields, vector=True)

