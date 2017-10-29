#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='poeditorcli',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click', 'PyYAML', 'requests', 'requests_toolbelt'
    ],
    entry_points='''
        [console_scripts]
        poeditorcli=poeditorcli.main:cli
    ''',
)
