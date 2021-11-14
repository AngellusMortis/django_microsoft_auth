from django.utils.translation import gettext_lazy as _

LOGIN_TYPE_MA = "ma"
LOGIN_TYPE_XBL = "xbl"

DEFAULT_CONFIG = {
    "defaults": {
        "MICROSOFT_AUTH_LOGIN_ENABLED": (
            True,
            _("Whether or not Microsoft OAuth login is enabled."),
            bool,
        ),
        "MICROSOFT_AUTH_LOGIN_TYPE": (
            LOGIN_TYPE_MA,
            _(
                """Type of Microsoft login to use.
                Microsoft Accounts is normal Microsoft login.
                Xbox Live Accounts use the old Microsoft Account login screen
                and then also authenticate against Xbox Live to retrieve
                Gamertag."""
            ),
            "microsoft_choices",
        ),
        "MICROSOFT_AUTH_TENANT_ID": (
            "common",
            _("Microsoft Office 365 Tenant ID"),
            str,
        ),
        "MICROSOFT_AUTH_CLIENT_ID": (
            "",
            _(
                """Microsoft OAuth Client ID, see
                https://apps.dev.microsoft.com/ for more."""
            ),
            str,
        ),
        "MICROSOFT_AUTH_CLIENT_SECRET": (
            "",
            _(
                """Microsoft OAuth Client Secret, see
                https://apps.dev.microsoft.com/ for more."""
            ),
            str,
        ),
        "MICROSOFT_AUTH_ASSERTION_CERTIFICATE": (
            "",
            _(
                """Microsoft OAuth Assertion Certificate, see
                https://docs.microsoft.com/en-us/azure/architecture
                /multitenant-identity/client-assertion for more."""
            ),
            str,
        ),
        "MICROSOFT_AUTH_ASSERTION_KEY": (
            "",
            _(
                """Microsoft OAuth Assertion Certificate, see
                https://docs.microsoft.com/en-us/azure/architecture
                /multitenant-identity/client-assertion for more."""
            ),
            str,
        ),
        "MICROSOFT_AUTH_EXTRA_SCOPES": (
            "",
            _(
                """Extra OAuth scopes for authentication. Required
                scopes are always provided ('openid email'
                for Microsoft Auth and 'XboxLive.signin
                XboxLive.offline_access' for Xbox). Scopes are space
                delimited."""
            ),
            str,
        ),
        "MICROSOFT_AUTH_AUTO_CREATE": (
            True,
            _(
                """Autocreate user that attempt to login if they do not
                already exist?"""
            ),
            bool,
        ),
        "MICROSOFT_AUTH_REGISTER_INACTIVE_ADMIN": (
            False,
            _(
                """Automatically register admin class for auth type
                that is not active (Xbox when Microsoft Auth is
                enabled and Microsoft Auth when Xbox is enabled).
                Requires restart of app for setting to take effect."""
            ),
            bool,
        ),
        "MICROSOFT_AUTH_XBL_SYNC_USERNAME": (
            False,
            _(
                """Automatically sync the username from the Xbox Live
                Gamertag?"""
            ),
            bool,
        ),
        "MICROSOFT_AUTH_AUTO_REPLACE_ACCOUNTS": (
            False,
            _(
                """Automatically replace an existing Microsoft Account
                paired to a user when authenticating."""
            ),
            bool,
        ),
        "MICROSOFT_AUTH_AUTHENTICATE_HOOK": (
            "",
            _(
                """Callable hook to call after authenticating a user on the
                `microsoft_auth.backends.MicrosoftAuthenticationBackend`.

                If the login type is Microsoft Auth, the parameters will be
                `(User: user, oauthlib.oauth2.rfc6749.tokens.OAuth2Token:
                token)`

                If the login type is Xbox Live, the parameters will be
                `(User:user, dict: token)` where token is the Xbox Token,
                see `microsoft_auth.client.MicrosoftClient.fetch_xbox_token`

                for format"""
            ),
            str,
        ),
        "MICROSOFT_AUTH_CALLBACK_HOOK": (
            "",
            _(
                """Callable hook to call right before completing the `auth_callback` view.

                Really useful for adding custom data to message or chaning the
                expected base URL that gets passed back up to the window that
                initiated the original Authorize request.

                The parameters that will be passed will be `(HttpRequest:
                request, dict: context)`.

                The expected return value is the updated context dictionary.
                You should NOT remove the data that is currently there.

                `base_url` is the expected root URL of the window that
                initiated the authorize request

                `message` is a dictionary that will be serialized as a JSON
                string and passoed back to the initiating window.
                """
            ),
            str,
        ),
        "MICROSOFT_AUTH_PROXIES": (
            {},
            _(
                """Use proxies for authentication
                See https://requests.readthedocs.io/en/master/user/advanced/#proxies/"""
            ),
            dict,
        ),
    },
    "fieldsets": {
        "Microsoft Login": (
            "MICROSOFT_AUTH_LOGIN_ENABLED",
            "MICROSOFT_AUTH_LOGIN_TYPE",
            "MICROSOFT_AUTH_TENANT_ID",
            "MICROSOFT_AUTH_CLIENT_ID",
            "MICROSOFT_AUTH_CLIENT_SECRET",
            "MICROSOFT_AUTH_EXTRA_SCOPES",
            "MICROSOFT_AUTH_AUTO_CREATE",
            "MICROSOFT_AUTH_REGISTER_INACTIVE_ADMIN",
            "MICROSOFT_AUTH_XBL_SYNC_USERNAME",
            "MICROSOFT_AUTH_AUTO_REPLACE_ACCOUNTS",
            "MICROSOFT_AUTH_AUTHENTICATE_HOOK",
            "MICROSOFT_AUTH_CALLBACK_HOOK",
        )
    },
    "fields": {
        "microsoft_choices": [
            "django.forms.fields.ChoiceField",
            {
                "widget": "django.forms.Select",
                "choices": (
                    (LOGIN_TYPE_MA, "Microsoft Auth"),
                    (LOGIN_TYPE_XBL, "Xbox Live"),
                ),
            },
        ]
    },
}
