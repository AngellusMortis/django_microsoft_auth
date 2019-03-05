#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from os import path

from setuptools import find_packages, setup

import versioneer

# for pip >= 10
try:
    from pip._internal.req import parse_requirements
# for pip <= 9.0.3
except ImportError:
    from pip.req import parse_requirements


BASE_DIR = path.abspath(path.dirname(__file__))

with open(path.join(BASE_DIR, "README.rst")) as readme_file:
    readme = readme_file.read()

with open(path.join(BASE_DIR, "HISTORY.rst")) as history_file:
    history = history_file.read()

req_files = {
    "dev": "reqs/dev.in",
    "ql": "reqs/ql.in",
    "requirements": "reqs/requirements.in",
    "setup": "reqs/setup.in",
    "test": "reqs/test.in",
}

requirements = {}
for req, req_file in req_files.items():
    reqs = parse_requirements(req_file, session="fake")
    requirements[req] = [str(req.req) for req in reqs]

setup(
    name="django_microsoft_auth",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description=(
        "Simple app to enable Microsoft Account, Office 365 "
        "Enterprise, Azure AD, and Xbox Live authentication as a "
        "Django authentication backend."
    ),
    long_description=readme + "\n\n" + history,
    author="Christopher Bailey",
    author_email="cbailey@mort.is",
    url="https://github.com/AngellusMortis/django_microsoft_auth",
    packages=find_packages(include=["microsoft_auth", "microsoft_auth.*"]),
    include_package_data=True,
    install_requires=requirements["requirements"],
    license="MIT license",
    zip_safe=False,
    keywords="django_microsoft_auth",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Framework :: Django :: 1.11",
        "Framework :: Django :: 2.0",
        "Framework :: Django :: 2.1",
    ],
    test_suite="tests",
    tests_require=requirements["test"],
    setup_requires=requirements["setup"],
    extras_require={
        "dev": requirements["dev"],
        "ql": requirements["ql"],
        "test": requirements["test"],
    },
)
