#!/usr/bin/env python

# standard library imports
from os.path import exists

# third party related imports
from setuptools import setup, find_packages

# local library imports
from elb_log_analyzer import __version__


def read_content(fn):

    if not exists(fn):
        return ''

    with open(fn) as f:
        return f.read()


setup(
    name='elb-log-analyzer',
    version=__version__,
    # Your name & email here
    author='Yu Liang',
    author_email='yu.liang@thekono.com',
    # If you had elb_log_analyzer.tests,
    # you would also include that in this list
    packages=find_packages(),
    # Any executable scripts, typically in 'bin'. E.g 'bin/do-something.py'
    scripts=[],
    # REQUIRED: Your project's URL
    url='https://github.com/yu-liang-kono/elb-log-analyzer',
    # Put your license here. See LICENSE.txt for more information
    license=read_content('LICENSE.txt'),
    # Put a nice one-liner description here
    description='A tool set to analyze AWS elb access log',
    long_description=read_content('README.md'),
    # Any requirements here, e.g. "Django >= 1.1.1"
    install_requires=read_content('requirements.txt').splitlines(),
)
