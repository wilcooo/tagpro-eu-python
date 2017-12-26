from setuptools import find_packages, setup

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_desc = f.read()

setup(
    name='tagpro-eu',
    version='1.0.0',
    license='GPL-3.0',

    packages=find_packages(),

    description='A Python parser for tagpro.eu matches',
    long_description=long_desc,
    url='https://github.com/arfie/tagpro-eu-python',
    author='Ruud Verbeek',

    keywords='tagpro',

    install_requires='requests',
    python_requires='>=3.6'
)
