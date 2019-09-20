from abc import abstractmethod
from pathlib import Path

from .core import Corpus


class BasePreprocessor:
    def __init__(self, corpus: Corpus):
        self._corpus = corpus

    @property
    def corpus(self):
        return self._corpus

    @abstractmethod
    def parse(self, file: Path):
        raise NotImplementedError
