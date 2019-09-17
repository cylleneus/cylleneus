import engine.analysis.filters
import engine.analysis.tokenizers
import engine.fields


PlainTextTokenizer = engine.analysis.tokenizers.CachedPlainTextTokenizer(chars=True)
LemmaFilter = engine.analysis.filters.CachedLemmaFilter()
SynsetFilter = engine.analysis.filters.CachedSynsetFilter()
AnnotationFilter = engine.analysis.filters.AnnotationFilter()
SemfieldFilter = engine.analysis.filters.SemfieldFilter()


class BaseSchema(engine.fields.SchemaClass):
    corpus = engine.fields.STORED()
    docix = engine.fields.STORED()
    author = engine.fields.STORED()
    title = engine.fields.STORED()
    filename = engine.fields.STORED()
    datetime = engine.fields.STORED()


class PlainTextDocumentSchema(BaseSchema):
    content = engine.fields.STORED()
    form = engine.fields.FORM(analyzer=PlainTextTokenizer, vector=True)
    lemma = engine.fields.LEMMA(analyzer=PlainTextTokenizer | LemmaFilter, vector=True)
    annotation = engine.fields.ANNOTATION(analyzer=PlainTextTokenizer | LemmaFilter | AnnotationFilter, vector=True)
    synset = engine.fields.SYNSET(analyzer=PlainTextTokenizer | LemmaFilter | SynsetFilter, vector=True)
    semfield = engine.fields.SEMFIELD(analyzer=PlainTextTokenizer | LemmaFilter | SynsetFilter | SemfieldFilter, vector=True)


PHI5Tokenizer = engine.analysis.tokenizers.CachedPHI5Tokenizer(chars=True)
class PHI5DocumentSchema(BaseSchema):
    urn = engine.fields.STORED()
    meta = engine.fields.STORED()
    content = engine.fields.STORED()
    form = engine.fields.FORM(analyzer=PHI5Tokenizer, vector=True)
    lemma = engine.fields.LEMMA(analyzer=PHI5Tokenizer | LemmaFilter, vector=True)
    annotation = engine.fields.ANNOTATION(analyzer=PHI5Tokenizer | LemmaFilter | AnnotationFilter, vector=True)
    synset = engine.fields.SYNSET(analyzer=PHI5Tokenizer | LemmaFilter | SynsetFilter, vector=True)
    semfield = engine.fields.SEMFIELD(analyzer=PHI5Tokenizer | LemmaFilter | SynsetFilter | SemfieldFilter, vector=True)


PerseusJSONTokenizer = engine.analysis.tokenizers.CachedPerseusJSONTokenizer(chars=True)
class PerseusJSONDocumentSchema(BaseSchema):
    urn = engine.fields.STORED()
    meta = engine.fields.STORED()
    form = engine.fields.FORM(analyzer=PerseusJSONTokenizer, vector=True)
    lemma = engine.fields.LEMMA(analyzer=PerseusJSONTokenizer | LemmaFilter, vector=True)
    annotation = engine.fields.ANNOTATION(analyzer=PerseusJSONTokenizer | LemmaFilter | AnnotationFilter, vector=True)
    synset = engine.fields.SYNSET(analyzer=PerseusJSONTokenizer | LemmaFilter | SynsetFilter, vector=True)
    semfield = engine.fields.SEMFIELD(analyzer=PerseusJSONTokenizer | LemmaFilter | SynsetFilter | SemfieldFilter, vector=True)


PerseusXMLTokenizer = engine.analysis.tokenizers.CachedPerseusXMLTokenizer(chars=True)
class PerseusXMLDocumentSchema(BaseSchema):
    urn = engine.fields.STORED()
    meta = engine.fields.STORED()
    form = engine.fields.FORM(analyzer=PerseusXMLTokenizer, vector=True)
    lemma = engine.fields.LEMMA(analyzer=PerseusXMLTokenizer | LemmaFilter, vector=True)
    annotation = engine.fields.ANNOTATION(analyzer=PerseusXMLTokenizer | LemmaFilter | AnnotationFilter, vector=True)
    synset = engine.fields.SYNSET(analyzer=PerseusXMLTokenizer | LemmaFilter | SynsetFilter, vector=True)
    semfield = engine.fields.SEMFIELD(analyzer=PerseusXMLTokenizer | LemmaFilter | SynsetFilter | SemfieldFilter, vector=True)


LASLATokenizer = engine.analysis.tokenizers.CachedLASLATokenizer(chars=True)
LASLALemmaFilter = engine.analysis.filters.CachedLASLALemmaFilter(chars=True)
class LASLADocumentSchema(BaseSchema):
    urn = engine.fields.STORED()
    meta = engine.fields.STORED()
    form = engine.fields.FORM(analyzer=LASLATokenizer, vector=True)
    lemma = engine.fields.LEMMA(analyzer=LASLATokenizer | LASLALemmaFilter, vector=True)
    annotation = engine.fields.ANNOTATION(analyzer=LASLATokenizer | LASLALemmaFilter | AnnotationFilter, vector=True)
    synset = engine.fields.SYNSET(analyzer=LASLATokenizer | LASLALemmaFilter | SynsetFilter, vector=True)
    semfield = engine.fields.SEMFIELD(analyzer=LASLATokenizer | LASLALemmaFilter | SynsetFilter | SemfieldFilter, vector=True)
    morphosyntax = engine.fields.MORPHOSYNTAX(analyzer=LASLATokenizer |
                                                            engine.analysis.filters.LASLAMorphosyntaxFilter(), vector=True)


PROIELTokenizer = engine.analysis.tokenizers.CachedPROIELTokenizer(chars=True)
PROIELLemmaFilter = engine.analysis.filters.CachedPROIELLemmaFilter(chars=True)
class PROIELDocumentSchema(BaseSchema):
    urn = engine.fields.STORED()
    meta = engine.fields.STORED()
    form = engine.fields.FORM(analyzer=PROIELTokenizer, vector=True)
    lemma = engine.fields.LEMMA(analyzer=PROIELTokenizer | PROIELLemmaFilter, vector=True)
    annotation = engine.fields.ANNOTATION(analyzer=PROIELTokenizer | PROIELLemmaFilter | AnnotationFilter, vector=True)
    synset = engine.fields.SYNSET(analyzer=PROIELTokenizer | PROIELLemmaFilter | SynsetFilter, vector=True)
    semfield = engine.fields.SEMFIELD(analyzer=PROIELTokenizer | PROIELLemmaFilter | SynsetFilter | SemfieldFilter, vector=True)
    morphosyntax = engine.fields.MORPHOSYNTAX(analyzer=PROIELTokenizer |
                                                            engine.analysis.filters.PROIELMorphosyntaxFilter(), vector=True)

AGLDTTokenizer = engine.analysis.tokenizers.CachedAGLDTTokenizer(chars=True)
AGLDTLemmaFilter = engine.analysis.filters.CachedAGLDTLemmaFilter(chars=True)
class AGLDTDocumentSchema(BaseSchema):
    urn = engine.fields.STORED()
    meta = engine.fields.STORED()
    form = engine.fields.FORM(analyzer=AGLDTTokenizer, vector=True)
    lemma = engine.fields.LEMMA(analyzer=AGLDTTokenizer | AGLDTLemmaFilter, vector=True)
    annotation = engine.fields.ANNOTATION(analyzer=AGLDTTokenizer | AGLDTLemmaFilter | AnnotationFilter, vector=True)
    synset = engine.fields.SYNSET(analyzer=AGLDTTokenizer | AGLDTLemmaFilter | SynsetFilter, vector=True)
    semfield = engine.fields.SEMFIELD(analyzer=AGLDTTokenizer | AGLDTLemmaFilter | SynsetFilter | SemfieldFilter, vector=True)
    morphosyntax = engine.fields.MORPHOSYNTAX(analyzer=AGLDTTokenizer |
                                                            engine.analysis.filters.AGLDTMorphosyntaxFilter(),
                                              vector=True)



schemas = {
    'agldt': AGLDTDocumentSchema,
    'imported': PlainTextDocumentSchema,
    'lasla': LASLADocumentSchema,
    'latin_library': PlainTextDocumentSchema,
    'phi5': PHI5DocumentSchema,
    'proiel': PROIELDocumentSchema,
    'perseus': PerseusJSONDocumentSchema,
    'perseus-xml': PerseusXMLDocumentSchema,
}
