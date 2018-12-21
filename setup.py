#!/usr/bin/env python3
from setuptools import find_packages, setup

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_desc = f.read()

setup(
    name='tagpro-eu',
    version='1.1.2',
    license='GPL-3.0',

    packages=find_packages(exclude=['test', 'examples']),

    description='A Python parser for tagpro.eu matches',
    long_description=long_desc,
    url='https://github.com/arfie/tagpro-eu-python',
    author='Ruud Verbeek',

    keywords='tagpro',

    install_requires='requests',
    python_requires='>=3.6',

    test_suite='test',

    py_modules=['tagpro_eu'],

    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',

        'Programming Language :: Python :: 3.6',

        'Topic :: Games/Entertainment',
    ]
)
