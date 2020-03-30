#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re

from setuptools import setup


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


version = get_version('drf_nested_formdata')

this_directory = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='drf_nested_formdata',
    version=version,
    url='http://github.com/emperorDuke/nested_formdata',
    download_url='http://github.com/emperorDuke/nested_formdata/archive/0.2.0.tar.gz',
    license='MIT',
    description='A library that parses nested json or form data to python object',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=['drf', 'nested_formdata', 'drf_nested_formdata', 'restframework', 'nested json'],
    author='Duke Effiom',
    author_email='effiomduke@gmail.com',
    packages=['drf_nested_formdata'],
    zip_safe=False,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'License :: OSI Approved :: MIT License',
    ], 
    test_suite='tests',
    tests_require=[
        'djangorestframework',
        'django'
    ]
)