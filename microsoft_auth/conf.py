from importlib import import_module

from django.test.signals import setting_changed
from django.utils.translation import ugettext_lazy as _

constance_config = None
settings = None

""" List of all possible default configs for microsoft_auth

    DEFAULT_CONFIG['defaults'] and DEFAULT_CONFIG['fieldsets'] are in a format
    usable by django-constance
    (https://django-constance.readthedocs.io/en/latest/) so these values can
    be directly added to the CONSTANCE_CONFIG and CONSTANCE_CONFIG_FIELDSETS
    in your global settings

    django-constance will also require the following field definition:

    CONSTANCE_ADDITIONAL_FIELDS = {
        'microsoft_choices': ['django.forms.fields.ChoiceField', {
            'widget': 'django.forms.Select',
            'choices': (('ma', 'Microsoft Accounts'),
                        ('xbl', 'Xbox Live Accounts'))}]}

    MICROSOFT_AUTH_CONFIG_CLASS is the only microsoft_auth setting not present
    here. See bottom of file for more on it.
"""

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
                `(User:user dict: token)` where token is the Xbox Token,
                see `microsoft_auth.client.MicrosoftClient.fetch_xbox_token`
                for format"""
            ),
            str,
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


class SimpleConfig:
    def __init__(self, config=None):
        self._defaults = {}
        if config:
            self.add_default_config(config)

    def add_default_config(self, config):
        tmp_dict = {}
        for key, value in config["defaults"].items():
            tmp_dict[key] = value[0]

        self._defaults.update(tmp_dict)

    def __getattr__(self, attr):
        val = None

        # Check Constance first if it is installed
        if constance_config:
            try:
                val = getattr(constance_config, attr)
            except AttributeError:
                pass

        if val is None:
            try:
                # Check if present in user settings
                val = getattr(settings, attr)
            except AttributeError:
                # Fall back to defaults
                try:
                    val = self._defaults[attr]
                except KeyError:
                    raise AttributeError

        return val


""" Override MICROSOFT_AUTH_CONFIG_CLASS to inject your own custom dynamic
    settings class into microsoft_auth. Useful if you want to manage config
    using a dynamic settings manager such as django-constance

    Optionally the class can have an 'add_default_config' method to add the
    above DEFAULT_CONFIG to config manager
"""
config = None


def init_config():
    global config, constance_config, settings

    from django.conf import settings as django_settings

    settings = django_settings

    # set constance config global
    if "constance" in settings.INSTALLED_APPS:
        from constance import config as constance_config
        from constance.signals import config_updated

        config_updated.connect(reload_settings)
    else:
        constance_config = None

    # retrieve and set config class
    if (
        hasattr(settings, "MICROSOFT_AUTH_CONFIG_CLASS")
        and settings.MICROSOFT_AUTH_CONFIG_CLASS is not None
    ):
        module, _, obj = settings.MICROSOFT_AUTH_CONFIG_CLASS.rpartition(".")
        conf = import_module(module)
        config = getattr(conf, obj)
        if hasattr(config, "add_default_config"):
            config.add_default_config(DEFAULT_CONFIG)
    else:
        config = SimpleConfig(DEFAULT_CONFIG)

    return config


init_config()


def reload_settings(*args, **kwargs):
    global config

    setting = kwargs.get("setting", kwargs.get("key"))

    # only reinitialize config if settings changed
    if setting.startswith("MICROSOFT_AUTH_"):
        init_config()


setting_changed.connect(reload_settings)
