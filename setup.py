#!/usr/bin/env python
import distribute_setup
distribute_setup.use_setuptools()

import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

from jira_oauth import get_version

setup(
    name = "django-jira-oauth",
    version = get_version(),
    description = "OAuth authentication with JIRA from Django",
    long_description = read("README.rst"),
    author = "Micah Carrick",
    author_email = "micah@quixotix.com",
    url = "https://github.com/MicahCarrick/django-jira-oauth",
    packages = find_packages(),
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "License :: OSI Approved :: MIT License"
    ],
    install_requires = [
        'requests-oauthlib'
    ],
)
