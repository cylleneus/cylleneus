from cylleneus.engine.analysis.filters import (
    AnnotationFilter,
    CachedLemmaFilter,
    CachedSynsetFilter,
    CaseFilter,
    SemfieldFilter,
)
from cylleneus.engine.fields import *
from cylleneus.engine.schemas import BaseSchema
from .tokenizer import CachedTokenizer

Tokens = CachedTokenizer(chars=True)
Lemmas = CachedLemmaFilter(chars=True)
Synsets = CachedSynsetFilter()
Annotations = AnnotationFilter()
Semfields = SemfieldFilter()


class DocumentSchema(BaseSchema):
    urn = STORED()
    meta = STORED()
    form = FORM(analyzer=Tokens | CaseFilter(), vector=True)
    lemma = LEMMA(analyzer=Tokens | Lemmas, vector=True)
    annotation = ANNOTATION(analyzer=Tokens | Lemmas | Annotations, vector=True)
    synset = SYNSET(analyzer=Tokens | Lemmas | Synsets, vector=True)
    semfield = SEMFIELD(analyzer=Tokens | Lemmas | Synsets | Semfields, vector=True)
