from engine.fields import *
from engine.schemas import BaseSchema
from engine.analysis.filters import CachedSynsetFilter, AnnotationFilter, SemfieldFilter, CaseFilter

from .tokenizer import CachedTokenizer
from .filters import CachedLemmaFilter, MorphosyntaxFilter


Tokens = CachedTokenizer(chars=True)
Lemmas = CachedLemmaFilter(chars=True)
Synsets = CachedSynsetFilter()
Annotations = AnnotationFilter()
Semfields = SemfieldFilter()
Morphosyntax = MorphosyntaxFilter()


class DocumentSchema(BaseSchema):
    urn = STORED()
    meta = STORED()
    form = FORM(analyzer=Tokens | CaseFilter(), vector=True)
    lemma = LEMMA(analyzer=Tokens | Lemmas, vector=True)
    annotation = ANNOTATION(analyzer=Tokens | Lemmas | Annotations, vector=True)
    synset = SYNSET(analyzer=Tokens | Lemmas | Synsets, vector=True)
    semfield = SEMFIELD(analyzer=Tokens | Lemmas | Synsets | Semfields, vector=True)
    morphosyntax = MORPHOSYNTAX(analyzer=Tokens | Morphosyntax, vector=True)
