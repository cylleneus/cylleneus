import engine.analysis.filters
import engine.analysis.tokenizers
import engine.fields

PlainTextTokenizer = engine.analysis.tokenizers.CachedPlainTextTokenizer(chars=True)
LemmaFilter = engine.analysis.filters.CachedLemmaFilter()
SynsetFilter = engine.analysis.filters.CachedSynsetFilter()
AnnotationFilter = engine.analysis.filters.AnnotationFilter()
SemfieldFilter = engine.analysis.filters.SemfieldFilter()
class PlainTextDocumentSchema(engine.fields.SchemaClass):
    author = engine.fields.STORED()
    title = engine.fields.STORED()
    content = engine.fields.STORED()
    filename = engine.fields.STORED()
    datetime = engine.fields.STORED()
    form = engine.fields.FORM(analyzer=PlainTextTokenizer, vector=True)
    lemma = engine.fields.LEMMA(analyzer=PlainTextTokenizer | LemmaFilter, vector=True)
    annotation = engine.fields.ANNOTATION(analyzer=PlainTextTokenizer | LemmaFilter | AnnotationFilter, vector=True)
    synset = engine.fields.SYNSET(analyzer=PlainTextTokenizer | LemmaFilter | SynsetFilter, vector=True)
    semfield = engine.fields.SEMFIELD(analyzer=PlainTextTokenizer | LemmaFilter | SynsetFilter | SemfieldFilter, vector=True)


class PlainTextDocumentSchema(engine.fields.SchemaClass):
    author = engine.fields.STORED()
    title = engine.fields.STORED()
    content = engine.fields.STORED()
    filename = engine.fields.STORED()
    datetime = engine.fields.STORED()
    form = engine.fields.FORM(analyzer=PlainTextTokenizer, vector=True)
    lemma = engine.fields.LEMMA(analyzer=PlainTextTokenizer | LemmaFilter, vector=True)
    annotation = engine.fields.ANNOTATION(analyzer=PlainTextTokenizer | LemmaFilter | AnnotationFilter, vector=True)
    synset = engine.fields.SYNSET(analyzer=PlainTextTokenizer | LemmaFilter | SynsetFilter, vector=True)
    semfield = engine.fields.SEMFIELD(analyzer=PlainTextTokenizer | LemmaFilter | SynsetFilter | SemfieldFilter, vector=True)


PHI5Tokenizer = engine.analysis.tokenizers.CachedPHI5Tokenizer(chars=True)
class PHI5DocumentSchema(engine.fields.SchemaClass):
    author = engine.fields.STORED()
    title = engine.fields.STORED()
    urn = engine.fields.STORED()
    meta = engine.fields.STORED()
    content = engine.fields.STORED()
    filename = engine.fields.STORED()
    datetime = engine.fields.STORED()
    form = engine.fields.FORM(analyzer=PHI5Tokenizer, vector=True)
    lemma = engine.fields.LEMMA(analyzer=PHI5Tokenizer | LemmaFilter, vector=True)
    annotation = engine.fields.ANNOTATION(analyzer=PHI5Tokenizer | LemmaFilter | AnnotationFilter, vector=True)
    synset = engine.fields.SYNSET(analyzer=PHI5Tokenizer | LemmaFilter | SynsetFilter, vector=True)
    semfield = engine.fields.SEMFIELD(analyzer=PHI5Tokenizer | LemmaFilter | SynsetFilter | SemfieldFilter, vector=True)


PerseusJSONTokenizer = engine.analysis.tokenizers.CachedPerseusJSONTokenizer(chars=True)
class PerseusJSONDocumentSchema(engine.fields.SchemaClass):
    author = engine.fields.STORED()
    title = engine.fields.STORED()
    filename = engine.fields.STORED()
    meta = engine.fields.STORED()
    filename = engine.fields.STORED()
    datetime = engine.fields.STORED()
    form = engine.fields.FORM(analyzer=PerseusJSONTokenizer, vector=True)
    lemma = engine.fields.LEMMA(analyzer=PerseusJSONTokenizer | LemmaFilter, vector=True)
    annotation = engine.fields.ANNOTATION(analyzer=PerseusJSONTokenizer | LemmaFilter | AnnotationFilter, vector=True)
    synset = engine.fields.SYNSET(analyzer=PerseusJSONTokenizer | LemmaFilter | SynsetFilter, vector=True)
    semfield = engine.fields.SEMFIELD(analyzer=PerseusJSONTokenizer | LemmaFilter | SynsetFilter | SemfieldFilter, vector=True)


PerseusTEITokenizer = engine.analysis.tokenizers.CachedPerseusTEITokenizer(chars=True)
class PerseusTEIDocumentSchema(engine.fields.SchemaClass):
    author = engine.fields.STORED()
    title = engine.fields.STORED()
    urn = engine.fields.STORED()
    meta = engine.fields.STORED()
    filename = engine.fields.STORED()
    datetime = engine.fields.STORED()
    form = engine.fields.FORM(analyzer=PerseusTEITokenizer, vector=True)
    lemma = engine.fields.LEMMA(analyzer=PerseusTEITokenizer | LemmaFilter, vector=True)
    annotation = engine.fields.ANNOTATION(analyzer=PerseusTEITokenizer | LemmaFilter | AnnotationFilter, vector=True)
    synset = engine.fields.SYNSET(analyzer=PerseusTEITokenizer | LemmaFilter | SynsetFilter, vector=True)
    semfield = engine.fields.SEMFIELD(analyzer=PerseusTEITokenizer | LemmaFilter | SynsetFilter | SemfieldFilter, vector=True)


LASLATokenizer = engine.analysis.tokenizers.CachedLASLATokenizer(chars=True)
LASLALemmaFilter = engine.analysis.filters.CachedLASLALemmaFilter(chars=True)
class LASLADocumentSchema(engine.fields.SchemaClass):
    author = engine.fields.STORED()
    title = engine.fields.STORED()
    urn = engine.fields.STORED()
    meta = engine.fields.STORED()
    filename = engine.fields.STORED()
    datetime = engine.fields.STORED()
    form = engine.fields.FORM(analyzer=LASLATokenizer, vector=True)
    lemma = engine.fields.LEMMA(analyzer=LASLATokenizer | LASLALemmaFilter, vector=True)
    annotation = engine.fields.ANNOTATION(analyzer=LASLATokenizer | LASLALemmaFilter | AnnotationFilter, vector=True)
    synset = engine.fields.SYNSET(analyzer=LASLATokenizer | LASLALemmaFilter | SynsetFilter, vector=True)
    semfield = engine.fields.SEMFIELD(analyzer=LASLATokenizer | LASLALemmaFilter | SynsetFilter | SemfieldFilter, vector=True)
    morphosyntax = engine.fields.MORPHOSYNTAX(analyzer=LASLATokenizer |
                                                            engine.analysis.filters.LASLAMorphosyntaxFilter(), vector=True)


# class PROIELXmlDocumentSchema(engine.fields.SchemaClass):
#     filename = engine.fields.STORED()
#     author = engine.fields.STORED()
#     title = engine.fields.STORED()
#     content = engine.fields.TEXT(analyzer=PlainTextTokenizer, chars=True, stored=True, vector=True)
#     form = engine.fields.FORM(analyzer=PlainTextTokenizer, vector=True)
#     lemma = engine.fields.LEMMA(analyzer=PlainTextTokenizer | LemmaFilter, stored=True, sortable=True, vector=True)
#     annotation = engine.fields.ANNOTATION(analyzer=PlainTextTokenizer | LemmaFilter | AnnotationFilter, stored=True, sortable=True, vector=True)
#     synset = engine.fields.SYNSET(analyzer=PlainTextTokenizer | LemmaFilter | SynsetFilter, stored=True, sortable=True, vector=True)
#     semfield = engine.fields.SEMFIELD(analyzer=PlainTextTokenizer | LemmaFilter | SynsetFilter | SemfieldFilter, stored=True, sortable=True, vector=True)


schemas = {
    'imported': PlainTextDocumentSchema,
    'lasla': LASLADocumentSchema,
    'latin_library': PlainTextDocumentSchema,
    'proiel': None,
    'phi5': PHI5DocumentSchema,
    'perseus': PerseusJSONDocumentSchema,
}
