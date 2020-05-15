from cylleneus.engine.fields import *
from cylleneus.engine.schemas import BaseSchema
from cylleneus.corpus.default import CachedTokenizer
from cylleneus.engine.analysis.filters import (
    CachedLemmaFilter,
    CachedSynsetFilter,
    AnnotationFilter,
    SemfieldFilter,
    CaseFilter,
)

Tokens = CachedTokenizer(chars=True)
Lemmas = CachedLemmaFilter(chars=True)
Synsets = CachedSynsetFilter()
Annotations = AnnotationFilter()
Semfields = SemfieldFilter()


class DocumentSchema(BaseSchema):
    form = FORM(analyzer=Tokens, vector=True)
    lemma = LEMMA(analyzer=Tokens | Lemmas, vector=True)
    annotation = ANNOTATION(
        analyzer=Tokens | Lemmas | Annotations, vector=True
    )
    synset = SYNSET(analyzer=Tokens | Lemmas | Synsets, vector=True)
    semfield = SEMFIELD(
        analyzer=Tokens | Lemmas | Synsets | Semfields, vector=True
    )
