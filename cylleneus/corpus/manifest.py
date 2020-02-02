from collections import namedtuple

from . import (
    agldt,
    atlas,
    default,
    lasla,
    latin_library,
    perseus,
    perseus_xml,
    proiel,
    translation_alignments,
    ramses
)


CorpusMeta = namedtuple(
    "CorpusMeta", ["schema", "tokenizer", "preprocessor", "glob", "fetch"]
)


meta = {
    "ramses": CorpusMeta(
        ramses.DocumentSchema,
        ramses.Tokenizer,
        ramses.Preprocessor,
        ramses.core.glob,
        ramses.core.fetch,
    ),
    "agldt":  CorpusMeta(
        agldt.DocumentSchema,
        agldt.Tokenizer,
        agldt.Preprocessor,
        agldt.core.glob,
        agldt.core.fetch,
    ),
    "atlas":  CorpusMeta(
        atlas.DocumentSchema,
        atlas.Tokenizer,
        atlas.Preprocessor,
        atlas.core.glob,
        atlas.core.fetch,
    ),
    "lasla": CorpusMeta(
        lasla.DocumentSchema,
        lasla.Tokenizer,
        lasla.Preprocessor,
        lasla.core.glob,
        lasla.core.fetch,
    ),
    "latin_library": CorpusMeta(
        latin_library.DocumentSchema,
        default.Tokenizer,
        latin_library.Preprocessor,
        latin_library.core.glob,
        latin_library.core.fetch,
    ),
    "perseus": CorpusMeta(
        perseus.DocumentSchema,
        perseus.Tokenizer,
        perseus.Preprocessor,
        perseus.core.glob,
        perseus.core.fetch,
    ),
    "perseus_xml": CorpusMeta(
        perseus_xml.DocumentSchema,
        perseus_xml.Tokenizer,
        perseus_xml.Preprocessor,
        perseus_xml.core.glob,
        perseus_xml.core.fetch,
    ),
    "translation_alignments": CorpusMeta(
        translation_alignments.DocumentSchema,
        translation_alignments.Tokenizer,
        translation_alignments.Preprocessor,
        translation_alignments.core.glob,
        translation_alignments.core.fetch,
    ),
    "proiel": CorpusMeta(
        proiel.DocumentSchema,
        proiel.Tokenizer,
        proiel.Preprocessor,
        proiel.core.glob,
        proiel.core.fetch,
    ),
    "default": CorpusMeta(
        default.DocumentSchema,
        default.Tokenizer,
        default.Preprocessor,
        default.glob,
        default.fetch,
    ),
}
