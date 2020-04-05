from collections import namedtuple

from . import default

from .lat import agldt, lasla, latin_library, perseus, perseus_xml, phi5, proiel
from .grk import atlas
from .eng import translation_alignments
from .skt import dcs

CorpusMeta = namedtuple(
    "CorpusMeta", ["language", "schema", "tokenizer", "preprocessor", "glob", "fetch", "repo"]
)

meta = {
    "agldt":                  CorpusMeta(
        agldt.core.language,
        agldt.DocumentSchema,
        agldt.Tokenizer,
        agldt.Preprocessor,
        agldt.core.glob,
        agldt.core.fetch,
        agldt.core.repo,
    ),
    "atlas": CorpusMeta(
        atlas.core.language,
        atlas.DocumentSchema,
        atlas.Tokenizer,
        atlas.Preprocessor,
        atlas.core.glob,
        atlas.core.fetch,
        atlas.core.repo
    ),
    "lasla": CorpusMeta(
        lasla.core.language,
        lasla.DocumentSchema,
        lasla.Tokenizer,
        lasla.Preprocessor,
        lasla.core.glob,
        lasla.core.fetch,
        lasla.core.repo
    ),
    "latin_library": CorpusMeta(
        latin_library.core.language,
        latin_library.DocumentSchema,
        default.Tokenizer,
        latin_library.Preprocessor,
        latin_library.core.glob,
        latin_library.core.fetch,
        latin_library.core.repo
    ),
    "perseus": CorpusMeta(
        perseus.core.language,
        perseus.DocumentSchema,
        perseus.Tokenizer,
        perseus.Preprocessor,
        perseus.core.glob,
        perseus.core.fetch,
        perseus.core.repo
    ),
    "perseus_xml": CorpusMeta(
        perseus_xml.core.language,
        perseus_xml.DocumentSchema,
        perseus_xml.Tokenizer,
        perseus_xml.Preprocessor,
        perseus_xml.core.glob,
        perseus_xml.core.fetch,
        perseus_xml.core.repo
    ),
    "translation_alignments": CorpusMeta(
        translation_alignments.core.language,
        translation_alignments.DocumentSchema,
        translation_alignments.Tokenizer,
        translation_alignments.Preprocessor,
        translation_alignments.core.glob,
        translation_alignments.core.fetch,
        translation_alignments.core.repo
    ),
    "proiel":                 CorpusMeta(
        proiel.core.language,
        proiel.DocumentSchema,
        proiel.Tokenizer,
        proiel.Preprocessor,
        proiel.core.glob,
        proiel.core.fetch,
        proiel.core.repo
    ),
    "dcs":                    CorpusMeta(
        dcs.core.language,
        dcs.DocumentSchema,
        dcs.Tokenizer,
        dcs.Preprocessor,
        dcs.core.glob,
        dcs.core.fetch,
        dcs.core.repo
    ),
    "default":                CorpusMeta(
        default.language,
        default.DocumentSchema,
        default.Tokenizer,
        default.Preprocessor,
        default.glob,
        default.fetch,
        default.repo
    ),
}
