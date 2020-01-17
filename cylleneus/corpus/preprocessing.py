from abc import abstractmethod
from pathlib import Path


class BasePreprocessor:
    def __init__(self, corpus):
        self._corpus = corpus

    @property
    def corpus(self):
        return self._corpus

    @abstractmethod
    def parse(self, file: Path):
        raise NotImplementedError
