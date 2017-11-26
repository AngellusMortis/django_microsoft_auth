#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from os import path

from setuptools import find_packages, setup

import versioneer

BASE_DIR = path.abspath(path.dirname(__file__))

with open(path.join(BASE_DIR, 'README.rst')) as readme_file:
    readme = readme_file.read()

with open(path.join(BASE_DIR, 'HISTORY.rst')) as history_file:
    history = history_file.read()

with open(path.join(BASE_DIR, 'requirements.in')) as f:
    requirements = f.read().split('\n')

with open(path.join(BASE_DIR, 'test-requirements.in')) as f:
    test_requirements = f.read().split('\n')

setup_requirements = [
    'pytest-runner',
]

setup(
    name='django_microsoft_auth',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="Simple app to enable Microsoft Account, Office 365 and Xbox Live authentcation as a Django authentcation backend.",
    long_description=readme + '\n\n' + history,
    author="Christopher Bailey",
    author_email='cbailey@mort.is',
    url='https://github.com/AngellusMortis/django_microsoft_auth',
    packages=find_packages(include=['microsoft_auth', 'microsoft_auth.*']),
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='django_microsoft_auth',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django :: 1.11',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
