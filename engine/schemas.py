from engine.fields import SchemaClass, STORED


class BaseSchema(SchemaClass):
    corpus = STORED()
    docix = STORED()
    author = STORED()
    title = STORED()
    filename = STORED()
    datetime = STORED()
