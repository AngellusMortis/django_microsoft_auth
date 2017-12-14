=======================================
Django Microsoft Authentication Backend
=======================================


.. image:: https://img.shields.io/pypi/v/django_microsoft_auth.svg
    :target: https://pypi.python.org/pypi/django_microsoft_auth
    :alt: PyPi

.. image:: https://img.shields.io/pypi/pyversions/django_microsoft_auth.svg
    :target: https://pypi.python.org/pypi/django_microsoft_auth
    :alt: Python Versions
 
.. image:: https://img.shields.io/travis/AngellusMortis/django_microsoft_auth.svg
    :target: https://travis-ci.org/AngellusMortis/django_microsoft_auth
    :alt: Travis CI

.. image:: https://readthedocs.org/projects/django-microsoft-auth/badge/?version=latest
    :target: https://django-microsoft-auth.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

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


Simple app to enable Microsoft Account, Office 365 and Xbox Live authentcation as a Django authentcation backend.


* Free software: MIT license
* Documentation: https://django-microsoft-auth.readthedocs.io.

Quickstart
----------

1. Install `Django <https://docs.djangoproject.com/en/1.11/topics/install/>`_
2. Install and configure the `Sites framework <https://docs.djangoproject.com/en/1.11/ref/contrib/sites/#enabling-the-sites-framework>`_
    - Make sure you update the domain of `SITE_ID`, this is important and used later. Easy way is to go `/admin/sites/site/1/change/` if you have the admin site enabled.
3. Create a `Microsoft OAuth Application <https://apps.dev.microsoft.com/>`_
    * write down your client ID
    * Generate an Application Secret, store this somewhere, you will need it for later
    * Add a `Web Platform` with `Allow Implicit Flow` and a valid Redirect URL (this will probably be `https://<your-domain>/microsoft/auth-callback/`), it **must be HTTPS**
    * Add `User.Read` under `Delegated Permissions`
4. Install package from PyPi::

    pip install django_microsoft_auth

5. Add the following to your `settings.py`::

    INSTALLED_APPS = [
        # other apps...
        'django.contrib.sites',
        'microsoft_auth',
    ]

    TEMPLATES = [
        {
            # other template settings...
            'OPTIONS': {
                'context_processors': [
                    # other context_processors...
                    'microsoft_auth.context_processors.microsoft',
                ],
            },
        },
    ]

    AUTHENTICATION_BACKENDS = [
        'microsoft_auth.backends.MicrosoftAuthenticationBackend',
        'django.contrib.auth.backends.ModelBackend' # if you also want to use Django's authentication
        # I recommend keeping this with at least one database superuser in case of unable to use others
    ]

    # pick one
    MICROSOFT_AUTH_LOGIN_TYPE = 'ma'  # Microsoft authentication
    # MICROSOFT_AUTH_LOGIN_TYPE = 'o365'  # Enterprise Office 365 authentication
    # MICROSOFT_AUTH_LOGIN_TYPE = 'xbl'  # Xbox Live authentication

    MICROSOFT_AUTH_CLIENT_ID = 'your-client-id-from-apps.dev.microsoft.com'
    MICROSOFT_AUTH_CLIENT_SECRET = 'your-client-secret-from-apps.dev.microsoft.com'

6. Add the following to your `urls.py`::

    urlpatterns = [
        # other urlpatterns...
        url(r'^microsoft/', include('microsoft_auth.urls', namespace='microsoft')),
    ]

7. Run migrations::

    python manage.py migrate

8. Start site and goto `/admin` to and logout if you are logged in.
9. Login as `Microsoft/Office 365/Xbox Live` user. It will fail. This will automatically create your new user.
10. Login as a `Password` user with access to change user accounts.
11. Go to `Admin -> Users` and edit your Microsoft user to have any permissions you want as you normally.
12. See `microsoft_auth/templates/microsoft/admin_login.html` for details examples on making a Login form.

See `official docs <https://django-microsoft-auth.readthedocs.io/en/latest/>`_ for more details on setup and configuration.

Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
