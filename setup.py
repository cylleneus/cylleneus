#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

import codecs
import os
import re
from pathlib import Path

from setuptools import find_packages, setup


with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    # intentionally *not* adding an encoding option to open, See:
    #   https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    with codecs.open(os.path.join(here, *parts), "r") as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M,
    )

    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


version = find_version("cylleneus", "__init__.py")

requirements = [
    "appdirs>=1.4.3",
    "certifi>=2019.11.28",
    "chardet>=3.0.4",
    "Click>=7.0",
    "click-spinner>=0.1.8",
    "cltk>=0.1.117",
    "future>=0.18.2",
    "gitpython>=3.1.0",
    "greekwordnet>=0.0.7",
    "idna>=2.8",
    "indic-transliteration>=1.9.4",
    "isodate>=0.6.0",
    "latinwordnet>=0.3.1",
    "LinkHeader>=0.4.3",
    "lxml>=4.4.2",
    "multiwordnet>=0.0.9",
    "MyCapytain>=3.0.0",
    "natsort>=7.0.0",
    "nltk>=3.4.5",
    "PyLD>=1.0.5",
    "pyparsing>=2.4.6",
    "python-docx>=0.8.10",
    "rdflib>=4.2.2",
    "rdflib-jsonld>=0.4.0",
    "requests>=2.22.0",
    "sanskritwordnet>=0.0.6",
    "six>=1.14.0",
    "tqdm>=4.41.1",
    "typing>=3.7.4.1",
    "urllib3>=1.25.7",
    "Whoosh>=2.7.4",
]

setup_requirements = ["appdirs>=1.4.3"]
test_requirements = []

setup(
    author="William Michael Short",
    author_email="w.short@exeter.ac.uk",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    description="Next-generation search engine for electronic corpora of ancient languages",
    entry_points={"console_scripts": ["cylleneus=cylleneus.cli:main", ], },
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="cylleneus",
    name="cylleneus",
    packages=find_packages(),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/cy/cylleneus",
    version=version,
    zip_safe=False,
)

from cylleneus.settings import CORPUS_DIR

corpus_dir = Path(CORPUS_DIR)
if not corpus_dir.exists():
    corpus_dir.mkdir(exist_ok=True, parents=True)
