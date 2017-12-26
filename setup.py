from setuptools import find_packages, setup

setup(
    name='tagpro-eu',
    version='1.0.0',
    license='GPL-3.0',

    packages=find_packages(),

    description='A Python parser for tagpro.eu matches',
    url='https://github.com/arfie/tagpro-eu-python',
    author='Ruud Verbeek',

    keywords='tagpro',

    install_requires='requests',
    python_requires='>=3.6'
)
