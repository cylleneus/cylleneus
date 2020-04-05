from cylleneus.engine.fields import *
from cylleneus.engine.schemas import BaseSchema
from cylleneus.engine.analysis.filters import SemfieldFilter, CaseFilter

from .tokenizer import CachedTokenizer
from .filters import CachedLemmaFilter, CachedSynsetFilter

Tokens = CachedTokenizer(chars=True)
Lemmas = CachedLemmaFilter(chars=True)
Synsets = CachedSynsetFilter()
Semfields = SemfieldFilter()


class DocumentSchema(BaseSchema):
    translator = STORED()
    urn = STORED()
    meta = STORED()
    form = FORM(analyzer=Tokens | CaseFilter(), vector=True)
    lemma = LEMMA(analyzer=Tokens | Lemmas, vector=True)
    synset = SYNSET(analyzer=Tokens | Lemmas | Synsets, vector=True)
    semfield = SEMFIELD(analyzer=Tokens | Lemmas | Synsets | Semfields, vector=True)
