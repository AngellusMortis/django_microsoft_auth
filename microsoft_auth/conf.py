from collections import OrderedDict
from importlib import import_module

from django.conf import settings
from django.test.signals import setting_changed
from django.utils.translation import ugettext_lazy as _

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
                        ('xbl', 'Xbox Live Accounts'),
                        ('o365', 'Office 365 Accounts'))}]}

    MICROSOFT_AUTH_CONFIG_CLASS is the only microsoft_auth setting not present
    here. See bottom of file for more on it.
"""

LOGIN_TYPE_MA = 'ma'
LOGIN_TYPE_O365 = 'o365'
LOGIN_TYPE_XBL = 'xbl'

DEFAULT_CONFIG = {
    'defaults': OrderedDict([
        ('MICROSOFT_AUTH_LOGIN_ENABLED', (
            True,
            _('Whether or not Microsoft OAuth login is enabled'),
            bool
        )),
        ('MICROSOFT_AUTH_LOGIN_TYPE', (
            LOGIN_TYPE_MA,
            _("""Type of Microsoft login to use.
                Microsoft Accounts is normal Microsoft login.
                Office 365 Accounts are for microsoftonline logins through
                    Office 365 groups and Microsoft Accounts (Microsoft
                    Accounts get redirected to separate login screen).
                Xbox Live Accounts use Microsoft Accounts and then also
                    authenticate against Xbox Live to retrieve Gamertag."""),
            'microsoft_choices'
        )),
        ('MICROSOFT_AUTH_CLIENT_ID', (
            '',
            _('Microsoft OAuth Client ID, see'
              'https://apps.dev.microsoft.com/ for more'),
            str
        )),
        ('MICROSOFT_AUTH_CLIENT_SECRET', (
            '',
            _('Microsoft OAuth Client Secret, see'
              'https://apps.dev.microsoft.com/ for more'),
            str
        )),
        ('MICROSOFT_AUTH_AUTO_CREATE', (
            True,
            _('Autocreate user that attempt to login if they do not '
              'already exist?'),
            bool
        )),
        ('MICROSOFT_AUTH_XBL_SYNC_USERNAME', (
            False,
            _('Automatically sync the username from the Xbox Live Gamertag?'),
            bool
        )),
    ]),
    'fieldsets': OrderedDict([
        ('Microsoft Login', (
            'MICROSOFT_AUTH_LOGIN_ENABLED',
            'MICROSOFT_AUTH_LOGIN_TYPE',
            'MICROSOFT_AUTH_CLIENT_ID',
            'MICROSOFT_AUTH_CLIENT_SECRET',))
    ])
}


class SimpleConfig:
    def __init__(self, config=None):
        self._defaults = {}
        if config:
            self.add_default_config(config)

    def add_default_config(self, config):
        if config['defaults']:
            tmp_dict = {}
            for key, value in config['defaults'].items():
                tmp_dict[key] = value[0]
            self._defaults.update(tmp_dict)

    def __getattr__(self, attr):
        val = None

        try:
            # Check if present in user settings
            val = getattr(settings, attr)
        except AttributeError:
            # Fall back to defaults
            val = self._defaults[attr]

        return val


""" Override MICROSOFT_AUTH_CONFIG_CLASS to inject your own custom dynamic
    settings class into microsoft_auth. Useful if you want to manage config
    using a dynamic settings manager such as django-constance

    Optionally the class can have an 'add_default_config' method to add the
    above DEFAULT_CONFIG to config manager
"""
config = None


def init_settings():
    global config
    if hasattr(settings, 'MICROSOFT_AUTH_CONFIG_CLASS') and \
            settings.MICROSOFT_AUTH_CONFIG_CLASS is not None:
        module, _, obj = settings.MICROSOFT_AUTH_CONFIG_CLASS.rpartition('.')
        conf = import_module(module)
        config = getattr(conf, obj)
        if hasattr(config, 'add_default_config'):
            config.add_default_config(DEFAULT_CONFIG)
    else:
        config = SimpleConfig(DEFAULT_CONFIG)


init_settings()


def reload_settings(*args, **kwargs):
    global config
    setting, _ = kwargs['setting'], kwargs['value']  # noqa
    if setting.startswith('MICROSOFT_AUTH_'):
        init_settings()


setting_changed.connect(reload_settings)
