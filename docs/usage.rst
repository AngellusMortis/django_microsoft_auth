=====
Usage
=====

Quickstart
----------

1. Install `Django <https://docs.djangoproject.com/en/stable/topics/install/>`_
2. Install and configure the `Sites framework <https://docs.djangoproject.com/en/stable/ref/contrib/sites/#enabling-the-sites-framework>`_

    .. important::

        **Make sure you update the domain in your `Site` object**

        This needs to match the host (hostname + port) that you are using to
        access the Django site with. The easiest way to do this to go to
        `/admin/sites/site/1/change/` if you have the admin site enabled.

        `SITE_ID` is only required if want to use the `MicrosoftClient` without
        a request object (all of the code provided in this package uses a request
        object). If you want multiple `Site` objects and generate authorize URL
        when accessing your site from multiple domains, you *must not* set a `SITE_ID`

3. Create a `Azure AD App <https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade>`_.
   After you register the app, make sure you click on "Certificates & Secrets"
   and generate a new Client Secret.

    .. important::

        You will need Client ID and an Client Secret for step 5. Make sure
        you generate these and store them somewhere. You will additionally need
        the Tenant ID if you configuring a single-tenant application.

        When you are registering the app it will ask for a Redirect URI. This
        **must** match the absolute URL of your `microsoft_auth:auth-callback`
        view. By default this would be `https://<your-domain>/microsoft/auth-callback/`.

        This URL **must be HTTPS** unless your hostname is `localhost`.
        `localhost` can **only** be used if `DEBUG` is set to `True`.
        Microsoft only allows HTTP authentication if the hostname is
        `localhost`.

4. Install package from PyPi

.. code-block:: console

    $ pip install django_microsoft_auth

5. Add the following to your `settings.py`

.. code-block:: python3

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

    # values you got from step 2 from your Mirosoft app
    MICROSOFT_AUTH_CLIENT_ID = 'your-client-id-from-apps.dev.microsoft.com'
    MICROSOFT_AUTH_CLIENT_SECRET = 'your-client-secret-from-apps.dev.microsoft.com'
    # Tenant ID is also needed for single tenant applications
    # MICROSOFT_AUTH_TENANT_ID = 'your-tenant-id-from-apps.dev.microsoft.com'

    # pick one MICROSOFT_AUTH_LOGIN_TYPE value
    # Microsoft authentication
    # include Microsoft Accounts, Office 365 Enterpirse and Azure AD accounts
    MICROSOFT_AUTH_LOGIN_TYPE = 'ma'

    # Xbox Live authentication
    MICROSOFT_AUTH_LOGIN_TYPE = 'xbl'  # Xbox Live authentication



6. Add the following to your `urls.py`

.. code-block:: python3

    urlpatterns = [
        # other urlpatterns...
        path('microsoft/', include('microsoft_auth.urls', namespace='microsoft')),
    ]

7. Run migrations

.. code-block:: console

    $ python manage.py migrate

8. Start site and goto `/admin` to and logout if you are logged in.
9. Login as `Microsoft/Office 365/Xbox Live` user. It will fail. This will
   automatically create your new user.
10. Login as a `Password` user with access to change user accounts.
11. Go to `Admin -> Users` and edit your Microsoft user to have any permissions
    you want as you normally.

Running behind a reverse-proxy
------------------------------

Make sure to pass your protocol with X-Forwarded-Proto so your callback url will be constructed properly

Redirect based authentication flow
----------------------------------

`django_microsoft_auth` provides views at `to-auth-redirect/` and
`from-auth-redirect/`, which can be used for customer facing authentication
without loading a JavaScript script to the page.

Redirect based authentication flow is triggered when user navigates to
`to-auth-redirect/`, which takes in an optional `next` query parameter,
for example, `to-auth-redirect/?next=/next/path`.
This parameter is passed to the Authentication provider in state variable.
After successfull authentication, authentication provider redirects the user to
`from-auth-redirect/`, which logs in the user, parses the state variable, and
redirects the user to the `next` path provided earlier or to `/` if no next path
was provided.

Test Site
---------

As part of unit testing, there minimal functioning site that is pimarily used
for running tests against and to help development. It can be used as a
reference for how to do some things.

The full refrence site exists under `tests/site`

To setup,

1. Make sure you have installed the project `from sources <installation.html#from-sources>`_.
2. Get a Microsoft app with a Client ID and Client Secret following step 3
   above.
3. Create a `tests/site/local.py` file and add your
   `MICROSOFT_AUTH_CLIENT_ID` and `MICROSOFT_AUTH_CLIENT_SECRET` settings
4. Start up the site

.. code-block:: console

    $ python -m tests.site migrate
    $ python -m tests.site createsuperuser
    $ python -m tests.site runserver

5. Configure your `Site <http://localhost:8000/admin/sites/site>`_.


Migrating from 1.0 to 2.0
-------------------------

`django_microsoft_auth` v2.0 changed the scopes that are used to retrieve user
data to fall inline with OpenID Connect standards. The old `User.read` scope is
now deprecated and `openid email profile` scopes are required by default.

This means the user ID that is returned from Microsoft has changed. To prevent
any possible data loss, out of the box, `django_microsoft_auth` will
essentially make it so you cannot log in with Microsoft auth to access any
users that are linked with a v1 Microsoft auth account.

You set `MICROSOFT_AUTH_AUTO_REPLACE_ACCOUNTS` to `True` to enable the behavior
that will automatically replace a paired Microsoft Account on a user with the
newly created one returned from Microsoft. This can potientally result is
orhpaned data if you have a related object references to `MicrosoftAccount`
instead of the user. It is recommend you stay on 1.3.x until you can manually
migrate this data.

Once these account have been migrated, you can safely delete any remaining
v1 Microsoft Accounts.

Sliencing `Scope has changed` warnings
--------------------------------------

If you stay on 1.3.x for a bit and you start getting
`Scope has changed from "User.Read" to "User.Read email profile openid".`, you
can slience this warning by setting an env variable for
`OAUTHLIB_RELAX_TOKEN_SCOPE` before starting Django.

Bash

```bash
$ export OAUTHLIB_RELAX_TOKEN_SCOPE=true
$ python manage.py runserver
```

PowerShell

```powershell
> $env:OAUTHLIB_RELAX_TOKEN_SCOPE=$TRUE
> python manage.py runserver
```

You should however upgrade to 2.0 once you can.
