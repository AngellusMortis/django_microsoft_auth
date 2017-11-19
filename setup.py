#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'django>=1.11,<2.0',
    'requests==2.18.4',
    'requests-oauthlib==0.8.0',
]

setup_requirements = [
    'pytest-runner',
    # TODO(AngellusMortis): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    'pytest',
    # TODO: put package test requirements here
]

setup(
    name='django_microsoft_auth',
    version='0.1.0',
    description="Simple app to enable Microsoft Account, Office 365 and Xbox Live authentcation as a Django authentcation backend.",
    long_description=readme + '\n\n' + history,
    author="Christopher Bailey",
    author_email='cbailey@mort.is',
    url='https://github.com/AngellusMortis/django_microsoft_auth',
    packages=find_packages(include=['microsoft_auth']),
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='django_microsoft_auth',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
