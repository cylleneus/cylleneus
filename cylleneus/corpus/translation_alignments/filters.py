import copy
import re

from cylleneus.engine.analysis.filters import Filter
from multiwordnet.wordnet import WordNet
from latinwordnet import LatinWordNet
from greekwordnet import GreekWordNet
from nltk.stem import WordNetLemmatizer

from latinwordnet.latinwordnet import relation_types

_iso_639 = {
    'en': 'english',
    'la': 'latin',
    'es': 'spanish',
    'he': 'hebrew',
    'it': 'italian',
    'fr': 'french'
}

EWN = WordNet("english")


class CachedLemmaFilter(Filter):
    is_morph = True

    def __init__(self, **kwargs):
        super(CachedLemmaFilter, self).__init__()
        self.cached = True
        self._cache = None
        self._docix = None
        self.__dict__.update(**kwargs)

    @property
    def cache(self):
        return copy.deepcopy(self._cache)

    def __eq__(self, other):
        return (other
                and self.__class__ is other.__class__
                and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self == other

    def __call__(self, tokens, **kwargs):
        if kwargs.get('docix', None) == self._docix and self._cache:
            yield from self.cache
        else:
            self._cache = []
            self._docix = kwargs.get('docix', None)

            EWN = WordNet("english")
            lemmatizer = WordNetLemmatizer()

            for t in tokens:
                if t.mode == 'index':
                    text = t.text.lower()
                    word = lemmatizer.lemmatize(text)

                    lemmas = EWN.get(word)
                    for lemma in lemmas:
                        t.text = f"{lemma.lemma}={lemma.pos}"
                        if self.cached:
                            self._cache.append(copy.copy(t))
                        yield t
                elif t.mode == 'query':
                    if '::' in t.text:
                        reltype, query = t.text.split('::')
                        t.reltype = reltype
                        t.text = query

                    text = t.text

                    if '#' in text:
                        yield t
                    elif '?' in text:
                        language, word = text.split('?')
                        t.language = language
                        t.text = word
                        yield t
                    else:
                        # </::love=VB>
                        if hasattr(t, 'reltype'):
                            keys = ['lemma', 'pos']
                            kwargs = {
                                k: v
                                for k, v in zip(
                                    keys,
                                    re.search(r"(\w+)(?:=(.+))?", text).groups()
                                )
                            }
                            if 'pos' in kwargs and kwargs['pos']:
                                kwargs['pos'] = {
                                    'NN':   'n',
                                    'VB':   'v',
                                    'ADJ':  'a',
                                    'ADV':  'r',
                                    'PREP': 'p'
                                }[kwargs['pos']]

                            if t.reltype in ['\\', '/', '+c', '-c']:
                                if t.reltype == '/':
                                    results = EWN.get_lemma(**kwargs).relatives
                                elif t.reltype == '\\':
                                    results = EWN.get_lemma(**kwargs).derivates
                                elif t.reltype == '+c':
                                    results = EWN.get_lemma(**kwargs).composes
                                else:
                                    results = EWN.get_lemma(**kwargs).composed_of
                            else:
                                # FIXME: This returns lexical not semantic relations!
                                lemma = EWN.get_lemma(**kwargs)
                                results = EWN.get_relations(w_source=lemma, type=t.reltype)
                            if results:
                                for result in results:
                                    if relation_types[t.reltype] in result['relations'].keys():
                                        for relation in result['relations'][relation_types[t.reltype]]:
                                            t.text = f"{relation['lemma']}={relation['morpho']}"
                                            yield t
                        else:
                            keys = ['lemma', 'pos']
                            kwargs = {
                                k: v
                                for k, v in zip(
                                    keys,
                                    re.search(r"(\w+)(?:=(.+))?", text).groups()
                                )
                            }
                            if 'pos' in kwargs and kwargs['pos']:
                                kwargs['pos'] = {
                                    'NN':   'n',
                                    'VB':   'v',
                                    'ADJ':  'a',
                                    'ADV':  'r',
                                    'PREP': 'p'
                                }[kwargs['pos']]

                            results = EWN.get(**kwargs)
                            for result in results:
                                t.text = f"{result.lemma}={result.pos}"
                                yield t


class CachedSynsetFilter(Filter):
    is_morph = True

    def __init__(self, **kwargs):
        super(CachedSynsetFilter, self).__init__()
        self._cache = None
        self._docix = None
        self.cached = True
        self.__dict__.update(**kwargs)

    @property
    def cache(self):
        return copy.deepcopy(self._cache)

    def __eq__(self, other):
        return (other
                and self.__class__ is other.__class__
                and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self == other

    def __call__(self, tokens, **kwargs):
        if kwargs.get('docix', None) == self._docix and self._cache:
            yield from self.cache
        else:
            self._cache = []
            self._docix = kwargs.get('docix', None)

            for t in tokens:
                if t.mode == 'index':
                    lemma, pos = t.text.split('=')

                    synsets = EWN.get_lemma(lemma=lemma, pos=pos).synsets
                    for synset in synsets:
                        t.code = ' '.join([semfield_mapping[semfield.english] for semfield in synset.semfield
                                           if semfield_mapping[semfield.english] is not None])
                        t.text = synset.id
                        if self.cached:
                            self._cache.append(copy.copy(t))
                        yield t
                elif t.mode == 'query':
                    if hasattr(t, 'language'):
                        language = t.language
                        text = t.text

                        if hasattr(t, 'reltype'):
                            for lemma in WordNet(_iso_639[language]).get(text):
                                if t.reltype in ['\\', '/', '+c', '-c']:
                                    lexical = True
                                else:
                                    lexical = False
                                for relation in WordNet(_iso_639[language]).get_relations(w_source=lemma,
                                                                                          type=t.reltype,
                                                                                          lexical=lexical):
                                    if relation.is_lexical:
                                        for synset in relation.w_target.synsets:
                                            t.text = synset.id
                                            yield t
                                    else:
                                        t.text = relation.id_target
                                        yield t
                        else:
                            if language == 'la':
                                for lemma in LatinWordNet().lemmas(lemma=text).synsets:
                                    for signification in lemma['synsets']:
                                        for synset in lemma['synsets'][signification]:
                                            t.text = f"{synset['pos']}#{synset['offset']}"
                                            yield t
                            elif language == 'gr':
                                for lemma in GreekWordNet().lemmas(lemma=text).synsets:
                                    for signification in lemma['synsets']:
                                        for synset in lemma['synsets'][signification]:
                                            t.text = f"{synset['pos']}#{synset['offset']}"
                                            yield t
                            else:
                                for lemma in WordNet(_iso_639[language]).get(text):
                                    for synset in lemma.synsets:
                                        t.text = synset.id
                                        yield t
                    elif '#' in t.text:  # raw synset
                        if hasattr(t, 'reltype'):
                            pos, offset = t.text.split('#')
                            result = EWN.synsets(pos, offset).relations
                            if t.reltype in result.keys():
                                for relation in result[t.reltype]:
                                    t.text = f"{relation['pos']}#{relation['offset']}"
                                    yield t
                        else:
                            yield t
                    else:
                        yield t


semfield_mapping = {
    "Factotum":               "None",
    "Number":                 "119",
    "Color":                  "535.6",
    "Time_Period":            "115",
    "Person":                 "757",
    "Quality":                "612",
    "Metrology":              "389",
    "Psychological_Features": "150",
    "Applied_Science":        "500",
    "Agriculture":            "630",
    "Animal_Husbandry":       "636",
    "Veterinary":             "591.2",
    "Food":                   "641",
    "Gastronomy":             "394.1",
    "Home":                   "640",
    "Architecture":           "720",
    "Town_Planning":          "307.1",
    "Buildings":              "690",
    "Furniture":              "684.1",
    "Computer_Science":       "004",
    "Engineering":            "620",
    "Mechanics":              "531",
    "Astronautics":           "510",
    "Electrotechnology":      "537",
    "Hydraulics":             "627",
    "Telecommunication":      "384",
    "Post":                   "383",
    "Telegraphy":             "384.1",
    "Telephony":              "384.6",
    "Medicine":               "610",
    "Dentistry":              "617.6",
    "Pharmacy":               "615",
    "Psychiatry":             "610",
    "Radiology":              "610",
    "Surgery":                "617",
    "Pure_Science":           "500",
    "Astronomy":              "520",
    "Biology":                "570",
    "Biochemistry":           "572",
    "Anatomy":                "611",
    "Physiology":             "612",
    "Genetics":               "576",
    "Animals":                "590",
    "Entomology":             "595.7",
    "Plants":                 "580",
    "Environment":            "363.7",
    "Chemistry":              "540",
    "Earth":                  "550",
    "Geology":                "551",
    "Meteorology":            "551.5",
    "Oceanography":           "551.4",
    "Paleontology":           "560",
    "Geography":              "910",
    "Topography":             "526",
    "Mathematics":            "510",
    "Geometry":               "516",
    "Statistics":             "519.5",
    "Physics":                "530",
    "Acoustics":              "534",
    "Atomic_Physic":          "539.7",
    "Electricity":            "537",
    "Electronics":            "621.3",
    "Gas":                    "533",
    "Optics":                 "535",
    "Social_Science":         "300",
    "Administration":         "351",
    "Anthropology":           "301",
    "Ethnology":              "301",
    "Folklore":               "398",
    "Artisanship":            "700",
    "Health":                 "613",
    "Body_Care":              "646.7",
    "Commerce":               "381",
    "Economy":                "330",
    "Enterprise":             "338.7",
    "Book_Keeping":           "657",
    "Finance":                "336",
    "Banking":                "332.1",
    "Money":                  "332.4",
    "Exchange":               "332.6",
    "Insurance":              "368",
    "Tax":                    "336.2",
    "Fashion":                "746.92",
    "Industry":               "338",
    "Law":                    "340",
    "Military":               "335",
    "Pedagogy":               "370",
    "School":                 "373",
    "University":             "378",
    "Politics":               "320",
    "Diplomacy":              "327.2",
    "Publishing":             "070",
    "Sexuality":              "306.7",
    "Sociology":              "301",
    "Tourism":                "910",
    "Transport":              "388",
    "Aviation":               "387",
    "Vehicles":               "388.3",
    "Nautical":               "387",
    "Railway":                "385",
    "Humanities":             "001.3",
    "History":                "900",
    "Heraldry":               "929.6",
    "Archaeology":            "930.1",
    "Linguistics":            "410",
    "Grammar":                "415",
    "Literature":             "800",
    "Philology":              "417",
    "Philosophy":             "100",
    "Psychology":             "150",
    "Psychoanalysis":         "362.2",
    "Art":                    "700",
    "Cinema":                 "791.4",
    "Dance":                  "793.3",
    "Drawing":                "740",
    "Graphic_Arts":           "760",
    "Philately":              "769",
    "Painting":               "750",
    "Music":                  "780",
    "Photography":            "770",
    "Plastic_Arts":           "730",
    "Jewelry":                "739",
    "Jewellery":              "739",
    "Numismatics":            "737",
    "Sculpture":              "731",
    "Theatre":                "792",
    "Religion":               "200",
    "Mythology":              "201",
    "Roman_Catholic":         "282",
    "Theology":               "230",
    "Ecology":                "577",
    "Alimentation":           "641",
    "Paranormal":             "130",
    "Occultism":              "130",
    "Astrology":              "133.5",
    "Free_Time":              "790",
    "Play":                   "795",
    "Betting":                "795.3",
    "Card":                   "795.4",
    "Chess":                  "794.1",
    "Radio_TV":               "791.4",
    "Sport":                  "796",
    "Badminton":              "796.3",
    "Baseball":               "796.3",
    "Basketball":             "796.3",
    "Cricket":                "796.3",
    "Football":               "796.3",
    "Golf":                   "796.3",
    "Rugby":                  "796.3",
    "Soccer":                 "796.3",
    "Table_Tennis":           "794.7",
    "Tennis":                 "796.3",
    "Volleyball":             "796.3",
    "Cycling":                "796.6",
    "Skating":                "796.9",
    "Skiing":                 "796.9",
    "Hockey":                 "796.9",
    "Mountaineering":         "796",
    "Rowing":                 "797.1",
    "Swimming":               "797.2",
    "Sub":                    "796.1",
    "Diving":                 "797.2",
    "Racing":                 "798",
    "Athletics":              "796",
    "Wrestling":              "796.5",
    "Boxing":                 "796.5",
    "Fencing":                "796.5",
    "Archery":                "796.5",
    "Fishing":                "799.1",
    "Hunting":                "799.2",
    "Bowling":                "794.6",
}
