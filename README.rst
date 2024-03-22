=======================================
Django Microsoft Authentication Backend
=======================================

Deprecated
----------

The point of this package was always to provide basic auth for the common Microsoft auth provider and Xbox Live auth. The common Microsoft auth provider has changed radically since I made this package and I really just do have any interest in updating it. If you want something that does Azure AD auth, go check out `django-auth-adfs <https://github.com/snok/django-auth-adfs>`.

-----------

.. image:: https://img.shields.io/pypi/v/django_microsoft_auth.svg
    :target: https://pypi.python.org/pypi/django_microsoft_auth
    :alt: PyPi

.. image:: https://img.shields.io/pypi/pyversions/django_microsoft_auth.svg
    :target: https://pypi.python.org/pypi/django_microsoft_auth
    :alt: Python Versions

.. image:: https://github.com/AngellusMortis/django_microsoft_auth/actions/workflows/ci.yml/badge.svg
    :target: https://github.com/AngellusMortis/django_microsoft_auth/actions/workflows/ci.yml
    :alt: CI

.. image:: https://readthedocs.org/projects/django-microsoft-auth/badge/?version=latest
    :target: https://django-microsoft-auth.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation

.. image:: https://api.codeclimate.com/v1/badges/ea41b61fa3a1e22e92e9/maintainability
   :target: https://codeclimate.com/github/AngellusMortis/django_microsoft_auth/maintainability
   :alt: Maintainability

.. image:: https://api.codeclimate.com/v1/badges/ea41b61fa3a1e22e92e9/test_coverage
   :target: https://codeclimate.com/github/AngellusMortis/django_microsoft_auth/test_coverage
   :alt: Test Coverage


Simple app to enable Microsoft Account, Office 365 and Xbox Live authentication
as a Django authentication backend.


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

`django_microsoft_auth` follows the same `support cycle as Django <https://www.djangoproject.com/download/#supported-versions>`_.

Supported python versions: 3.8+

Supported Django version: 3.2+

https://docs.djangoproject.com/en/stable/faq/install/#what-python-version-can-i-use-with-django


Credits
-------

This package was created with Cookiecutter_ and the
`audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
