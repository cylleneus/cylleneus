from cylleneus.engine.fields import SchemaClass, STORED


class BaseSchema(SchemaClass):
    corpus = STORED()
    docix = STORED()
    author = STORED()
    title = STORED()
    language = STORED()
    filename = STORED()
    datetime = STORED()
