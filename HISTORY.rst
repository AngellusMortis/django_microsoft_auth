=======
History
=======

2.4.0 (2020-8-14)
----------------

* Add support for Django 3.0 & 3.1
* Dropped support for Django 1.11
* Fixes error in name parsing
  - Fixes crash arising from missing comma in fullname
  - Assigns fullname to firstname if it can't be split
* Fixes installation with latest pip
* Fixes OpenID library crash due to uninitialized jwk

2.3.1 (2019-7-20)
-----------------

* Fixes W002 being displayed if you set the SITE_ID setting
* Fixes migration except for non-SQLite DBs

2.3.0 (2019-6-2)
-----------------

* Adds Django cache support for OIDC config/JWKS

2.2.3 (2019-5-19)
-----------------

* Django settings trump Constance settings always now
* Fixes `microsoft.conf.config` not using Constance in some cases

2.2.2 (2019-5-8)
----------------

* Fixes Javascript typo

2.2.1 (2019-4-28)
-----------------

* Namespaces messages passed back as part of login

2.2.0 (2019-3-26)
-----------------

* Adds new setting for callback hook right before `auth_callback` view renders
  to override context data
* Adds example non-admin login form example in test site
* Renames `admin_login.js` and `admin_login.css` to just `login.js` and
  `login.css`

2.1.1 (2019-3-24)
-----------------

* Adds profile back as a default scope since Microsoft is added if it is not

2.1.0 (2019-3-23)
-----------------

* Adds support for multiple SITE_IDs. If the setting is not provided, it will
  pull it from the request object
* Adds new setting for callback hook after
  `microsoft_auth.backends.MicrosoftAuthenticationBackend` authenticates user.

2.0.1 (2019-3-19)
-----------------

* Removes `profile` from required scopes

2.0.0 (2019-3-19)
-----------------

* Replaces deprecated Microsoft auth scopes with proper OpenID Connect ones
    * WARNING: Breaking change. New scopes provide a new user id. See
      `migration docs <https://django-microsoft-auth.readthedocs.io/en/latest/usage.html#migrating-from-1-0-to-2-0>`_
      for details.
* Pulls authorization/token URLs directly from Microsoft
* Adds id token validation
* Admin pages for the auth type that is not enable is disabled by default now.
  They can be re-enabled with `MICROSOFT_AUTH_REGISTER_INACTIVE_ADMIN = True`
* Extra scopes can be provieded via the `MICROSOFT_AUTH_EXTRA_SCOPES` setting
  (space delimited). These scopes are *added* to the default required scopes
  (`openid email` for Microsoft Auth and
  `XboxLive.signin XboxLive.offline_access` for Xbox Live auth)

1.3.3 (2019-3-16)
-----------------

* Adds expiration to state values (hardcoded 5 minutes)

1.3.2 (2019-3-16)
-----------------

* Changes state validation to use cryptographic signing now. State
  validation should be signfincally more relaible now.

1.3.1 (2019-3-16)
-----------------

* Adds more logging around CSRF/State failures

1.3.0 (2019-3-5)
----------------

* Adds support for other tenant IDs for Microsoft
  authentication (thanks aviv)

1.2.1 (2019-2-28)
-----------------

* Adds missing migration for changing `microsoft_id` from 32 to 36 length

1.2.0 (2019-1-13)
-----------------

* Adds various checks and logging to validate setup to help with debugging
* Adds support for `http://localhost` as a redirect URI base if `DEBUG` is
  enabled
* Fixes Javascript message passing if using a non-standard port (something
  other than 80 or 443)

1.1.0 (2018-7-3)
----------------
* Removes o365 option. New authorization URL works well enough for both
    * Xbox Live Auth still uses old Microsoft Auth URL
    * 'o365' will still work as a MICROSOFT_AUTH_LOGIN_TYPE value,
      but you should change it to 'ma'
* Adds extras:
    * `ql`: DjangoQL package and support
    * `test`: test dependencies (same as test_requires packages)
    * `dev`: `ql`+`test` and extra dev only dependencies like
      `twine` and `pip-tools`
* Pip 10 support (thanks Shigumitsu!)
* Fixes max length of o365 IDs (thanks Shigumitsu!)

1.0.6 (2018-4-8)
----------------
* Added patched username validator to allow spaces for usernames for
  Xbox Live Gamertags

1.0.5 (2018-4-8)
----------------
* Added missing templates and static files to MANIFEST

1.0.4 (2017-12-2)
-----------------

* Updated Django category to include 2.0

1.0.3 (2017-12-2)
-----------------

* Updated for Django 2.0

1.0.2 (2017-11-27)
------------------

* Changed Development Status category to Stable

1.0.0 (2017-11-19)
------------------

* First release on PyPI.
