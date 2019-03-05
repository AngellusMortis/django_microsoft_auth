=======================================
Django Microsoft Authentication Backend
=======================================


.. image:: https://img.shields.io/pypi/v/django_microsoft_auth.svg
    :target: https://pypi.python.org/pypi/django_microsoft_auth
    :alt: PyPi

.. image:: https://img.shields.io/pypi/pyversions/django_microsoft_auth.svg
    :target: https://pypi.python.org/pypi/django_microsoft_auth
    :alt: Python Versions

.. image:: https://travis-ci.org/AngellusMortis/django_microsoft_auth.svg?branch=master
    :target: https://travis-ci.org/AngellusMortis/django_microsoft_auth/
    :alt: Travis CI

.. image:: https://readthedocs.org/projects/django-microsoft-auth/badge/?version=latest
    :target: https://django-microsoft-auth.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation

.. image:: https://pyup.io/repos/github/AngellusMortis/django_microsoft_auth/shield.svg
    :target: https://pyup.io/repos/github/AngellusMortis/django_microsoft_auth/
    :alt: Updates

.. image:: https://coveralls.io/repos/github/AngellusMortis/django_microsoft_auth/badge.svg?branch=master
    :target: https://coveralls.io/github/AngellusMortis/django_microsoft_auth?branch=master
    :alt: Coverage

.. image:: https://api.codeclimate.com/v1/badges/ea41b61fa3a1e22e92e9/maintainability
   :target: https://codeclimate.com/github/AngellusMortis/django_microsoft_auth/maintainability
   :alt: Maintainability

.. image:: https://api.codeclimate.com/v1/badges/ea41b61fa3a1e22e92e9/test_coverage
   :target: https://codeclimate.com/github/AngellusMortis/django_microsoft_auth/test_coverage
   :alt: Test Coverage


Simple app to enable Microsoft Account, Office 365 and Xbox Live authentcation
as a Django authentcation backend.


* Free software: MIT license
* Documentation: https://django-microsoft-auth.readthedocs.io.

Features
--------

* Provides Django authentication backend to do Microsoft authentication
  (including Microsoft accounts, Office 365 accounts and Azure AD accounts)
  and Xbox Live authentication.

* Provides Microsoft OAuth client to interfacing with Microsoft accounts

Python/Django support
---------------------

`django_microsoft_auth` follows the same `support cycle as Django <https://www.djangoproject.com/download/#supported-versions>`_,
with one exception: no Python 2 support. If you absoutely need Python 2.7
support, everything should largely already work, but you may need to patch
`microsoft_auth.admin` and/or other files to get it to work.

Supported python versions:  3.4+ (for Django versions less than 2.1)

Supported Django version: 1.11 LTS, 2.0+

Credits
-------

This package was created with Cookiecutter_ and the
`audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
