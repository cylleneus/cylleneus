#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

import sys

import config
from setuptools import find_packages, setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    'certifi>=2019.3.9',
    'chardet>=3.0.4',
    'cltk>=0.1.107',
    'cursor>=1.3.4',
    'future>=0.17.1',
    'idna>=2.8',
    'isodate>=0.6.0',
    'latinwordnet>=0.0.9',
    'lxml>=4.3.2',
    'MyCapytain>=2.0.10',
    'multiwordnet>=0.0.2',
    'nltk>=3.4',
    'parawrap>=1.0',
    'pyparsing>=2.3.1',
    'pyrsistent>=0.14.11',
    'python-crfsuite>=0.9.6',
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
    'Whoosh>=2.7.4',
]

if sys.platform == 'win32':
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
    version=config.__version__,
    zip_safe=False,
)
