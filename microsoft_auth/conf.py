from importlib import import_module
from collections import OrderedDict

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

""" List of all possible default configs for microsoft_auth

    DEFAULT_CONFIG['defaults'] and DEFAULT_CONFIG['fieldsets'] are in a format
    usable by django-constance (https://django-constance.readthedocs.io/en/latest/)
    so these values can be directly added to the CONSTANCE_CONFIG and
    CONSTANCE_CONFIG_FIELDSETS in your global settings

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
DEFAULT_CONFIG = {
    'defaults': OrderedDict([
        ('MICROSOFT_AUTH_LOGIN_ENABLED', (
            True,
            _('Whether or not Microsoft OAuth login is enabled'),
            bool)),
        ('MICROSOFT_AUTH_LOGIN_TYPE', (
            'ma',
            _("""Type of Microsoft login to use.
                Microsoft Accounts is normal Microsoft login.
                Office 365 Accounts are for microsoftonline logins through
                    Office 365 groups and Microsoft Accounts (Microsoft
                    Accounts get redirected to separate login screen).
                Xbox Live Accounts use Microsoft Accounts and then also
                    authenticate against Xbox Live to retrieve Gamertag."""),
            'microsoft_choices')),
        ('MICROSOFT_AUTH_CLIENT_ID', (
            '',
            _('Microsoft OAuth Client ID, see'
              'https://apps.dev.microsoft.com/ for more'),
            str)),
        ('MICROSOFT_AUTH_CLIENT_SECRET', (
            '',
            _('Microsoft OAuth Client Secret, see'
              'https://apps.dev.microsoft.com/ for more'),
            str))
    ]),
    'fieldsets': OrderedDict([
        ('Microsoft Login', (
            'MICROSOFT_AUTH_LOGIN_ENABLED',
            'MICROSOFT_AUTH_LOGIN_TYPE',
            'MICROSOFT_AUTH_CLIENT_ID',
            'MICROSOFT_AUTH_CLIENT_SECRET',))
    ])
}

""" Override MICROSOFT_AUTH_CONFIG_CLASS to inject your own custom dynamic
    settings class into microsoft_auth. Useful if you want to manage config
    using a dynamic settings manager such as django-constance

    Optionally the class can have an 'add_default_config' method to add the
    above DEFAULT_CONFIG to config manager
"""
if hasattr(settings, 'MICROSOFT_AUTH_CONFIG_CLASS'):
    module, _, obj = settings.MICROSOFT_AUTH_CONFIG_CLASS.rpartition('.')
    conf = import_module(module)
    config = getattr(conf, obj)
    if hasattr(config, 'add_default_config'):
        config.add_default_config(DEFAULT_CONFIG)
else:
    config = settings
