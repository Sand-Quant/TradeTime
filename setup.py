#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Author : SandQuant
# @Email: data@sandquant.com

import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

packages = ['tradetime']
requires = ['pandas', 'sandinvest']

info = {}
with open(os.path.join(here, 'tradetime', '__version__.py'), 'r', encoding='utf-8') as _version:
    exec(_version.read(), info)

with open("README.md", "r", encoding="utf-8") as _readme:
    readme = _readme.read()

setup(
    name=info['__module__'],
    version=info['__version__'],
    description=info['__description__'],
    long_description=readme,
    long_description_content_type='text/markdown',
    author=info['__author__'],
    author_email=info['__email__'],
    packages=packages,
    install_requires=requires,
    include_package_data=True,
    python_requires='>=3.5',
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: Chinese (Simplified)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    keywords=['Trade', 'Datetime'],
)
