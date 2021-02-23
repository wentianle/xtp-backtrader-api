#!/usr/bin/env python

import ast
import os
import re
from setuptools import setup

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('xtp_backtrader_api/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

with open('README.md') as readme_file:
    README = readme_file.read()

with open(os.path.join("requirements", "requirements.txt")) as reqs:
    REQUIREMENTS = reqs.readlines()

with open(os.path.join("requirements", "requirements_test.txt")) as reqs:
    REQUIREMENTS_TEST = reqs.readlines()


setup(
    name='xtp-backtrader-api',
    version=version,
    description='XTP API within backtrader',
    long_description=README,
    long_description_content_type='text/markdown',
    author='XTP',
    author_email='oss@xtp.markets',
    url='https://github.com/wentianle/xtp-backtrader-api',
    keywords='financial,timeseries,api,trade,backtrader',
    packages=['xtp_backtrader_api'],
    install_requires=REQUIREMENTS,
    tests_require=REQUIREMENTS_TEST,
    setup_requires=['pytest-runner', 'flake8'],
)
