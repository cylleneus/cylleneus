#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

import codecs
import os
import re

import settings
from setuptools import find_packages, setup


here = os.path.abspath(os.path.dirname(__file__))

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()


def read(*parts):
    # intentionally *not* adding an encoding option to open, See:
    #   https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]",
        version_file,
        re.M,
    )

    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


version = find_version('cylleneus', '__init__.py')

requirements = [
    'Click>=6.0',
    'certifi>=2019.3.9',
    'celery[redis]>=4.3.0',
    'chardet>=3.0.4',
    'click-spinner>=0.1.8',
    'cursor>=1.3.4',
    'fastapi>=0.42.0',
    'fastnumbers>=2.2.1',
    'flask>=1.1.1',
    'future>=0.17.1',
    'greekwordnet>=0.0.1',
    'html3>=1.17',
    'idna>=2.8',
    'isodate>=0.6.0',
    'latinwordnet>=0.2.4',
    'librabbitmq>=2.0.0',
    'lxml>=4.3.2',
    'MyCapytain>=2.0.10',
    'multiwordnet>=0.0.4',
    'natsort>=6.0.0',
    'nltk>=3.4',
    'parawrap>=1.0',
    'peewee>=3.10.0',
    'pyparsing>=2.3.1',
    'pyrsistent>=0.14.11',
    'python-crfsuite>=0.9.6',
    'python-docx>=0.8.10',
    'pyuca>=1.2',
    'rdflib>=4.2.2',
    'rdflib-jsonld>=0.4.0',
    'regex>=2019.3.12',
    'requests>=2.21.0',
    'riposte>=0.3.0',
    'singledispatch>=3.4.0.3',
    'six>=1.12.0',
    'tqdm>=4.31.1',
    'urllib3<1.25,>=1.21.1',
    'uvicorn>=0.10.8',
    'Whoosh>=2.7.4',
]

if settings.PLATFORM == 'win32':
    requirements.append('pyreadline>=2.1')

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="William Michael Short",
    author_email='w.short@exeter.ac.uk',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Next-generation search engine for electronic corpora of Greek and Latin",
    entry_points={
        'console_scripts': [
            'cylleneus=cylleneus.cli:main',
        ],
    },
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='cylleneus',
    name='cylleneus',
    packages=find_packages(exclude=['corpus/lasla/text']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/wmshort/cylleneus',
    version=version,
    zip_safe=False,
)
