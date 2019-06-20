import requests


class Semfields:
    def __init__(self, host, code=None, english=None):
        self.host = host
        self.code = code
        self.english = english
        self.json = None

    def get(self):
        if self.json is None:
            self.json = requests.request('GET', f"{self.host}/semfields/{self.code}/?format=json").json()
        return self.json

    def search(self):
        if self.english:
            return requests.request('GET', f"{self.host}/semfields?search={self.english}").json()['results']
        else:
            return None

    # def __repr__(self):
    #     return requests.request('GET', f"{self.host}/semfields/{self.code}/?format=json").json()

    def __iter__(self):
        return iter(self.get())

    @property
    def lemmas(self):
        return iter(requests.request('GET', f"{self.host}/semfields/{self.code}/lemmas/?format=json").json())

    @property
    def relations(self):
        return iter(requests.request('GET', f"{self.host}/semfields/{self.code}/synsets/?format=json").json())


class Synsets:
    def __init__(self, host, pos=None, offset=None, gloss=None):
        self.host = host
        self.offset = f"{offset}/" if offset else '*/'
        self.pos = f"{pos}/" if pos else '*/'
        self.gloss = gloss
        self.json = None

    def get(self):
        if self.json is None:
            self.json = requests.request('GET', f"{self.host}/synsets/{self.pos}{self.offset}?format=json").json()
        return self.json

    def search(self):
        if self.gloss:
            return requests.request('GET', f"{self.host}/synsets?search={self.lemma}").json()['results']
        else:
            return None

    # def __repr__(self):
    #     return requests.request('GET', f"{self.host}/synsets/{self.pos}/{self.offset}/?format=json").json()

    def __iter__(self):
        return iter(self.get())

    @property
    def lemmas(self):
        return requests.request('GET', f"{self.host}/synsets/{self.pos}{self.offset}lemmas/?format=json").json()

    @property
    def relations(self):
        return requests.request('GET', f"{self.host}/synsets/{self.pos}{self.offset}relations/?format=json").json()['relations']


class Lemmas:
    def __init__(self, host, lemma=None, pos=None, morpho=None):
        self.host = host
        self.lemma = f"{lemma}/" if lemma else '*/'
        self.pos = f"{pos}/" if pos else '*/'
        self.morpho = f"{morpho}/" if morpho else ''
        self.json = None

    def get(self):
        if self.json is None:
            self.json = requests.request('GET', f"{self.host}/lemmas/{self.lemma}{self.pos}{self.morpho}?format=json").json()
        return self.json

    def search(self):
        if self.lemma:
            return requests.request('GET', f"{self.host}/lemmas?search={self.lemma}").json()['results']
        else:
            return None

    # def __repr__(self):
    #     return requests.request('GET', f"{self.host}/lemmas/{self.lemma}{self.pos}{self.morpho}?format=json").json()

    def __iter__(self):
        return iter(self.get())

    @property
    def synsets(self):
        return requests.request('GET', f"{self.host}/lemmas/{self.lemma}{self.pos}{self.morpho}synsets/?format=json").json()

    @property
    def relations(self):
        return requests.request('GET', f"{self.host}/lemmas/{self.lemma}{self.pos}{self.morpho}relations/?format=json").json()

    @property
    def synsets_relations(self):
        return requests.request('GET', f"{self.host}/lemmas/{self.lemma}{self.pos}{self.morpho}synsets/relations/?format=json").json()


class LatinWordNet:
    def __init__(self, host='http://latinwordnet.exeter.ac.uk'):
        self.host = host.rstrip('/')

    def lemmatize(self, form: str):
        results = requests.request('GET', f"{self.host}/lemmatize/{form}/?format=json")
        return iter(results.json()) if results else None

    def translate(self, language: str, form: str, pos: str='*'):
        pos = f"{pos}/" if pos else ''
        results = requests.get(f"{self.host}/translate/{language}/{form}/{pos}?format=json")
        return iter(results.json()) if results else None

    def lemmas(self, lemma=None, pos=None, morpho=None):
        return Lemmas(self.host, lemma, pos, morpho)

    def synsets(self, pos: str, offset: str=None, gloss: str=None):
        return Synsets(self.host, pos, offset, gloss)

    def semfields(self, code: str=None, english: str=None):
        return Semfields(self.host, code, english)

    def index(self, pos=None, morpho=None):
        pos = f"{pos}/" if pos else '*/'
        morpho = f"{morpho}/" if morpho else ''
        results = requests.request('GET', f"{self.host}/index/{pos}{morpho}/?format=json")
        return iter(results.json()) if results else None
