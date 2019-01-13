from django.apps import AppConfig, apps
from django.core.checks import Critical, Warning, register
from django.db.utils import OperationalError


class MicrosoftAuthConfig(AppConfig):
    name = 'microsoft_auth'
    verbose_name = 'Microsoft Auth'


@register()
def microsoft_auth_validator(app_configs, **kwargs):
    from django.contrib.sites.models import Site
    from .conf import config

    errors = []

    if apps.is_installed('microsoft_auth') and \
            not apps.is_installed('django.contrib.sites'):

        errors.append(
            Critical(
                '`django.contrib.sites` is not installed',
                hint=('`microsoft_auth` requires `django.contrib.sites` '
                      'to be installed and configured'),
                id='microsoft_auth.E001',
            )
        )

    try:
        config.SITE_ID
    except KeyError:
        errors.append(
            Critical(
                'current site not configured',
                hint=('`django.contrib.sites` requires a `SITE_ID` setting '
                      'to be set'),
                id='microsoft_auth.E002',
            )
        )
    else:
        try:
            current_site = Site.objects.get_current()
        except OperationalError:
            errors.append(
                Warning(
                    '`django.contrib.sites` migrations not ran',
                    id='microsoft_auth.W001',
                )
            )
        else:
            if str(current_site) == 'example.com':
                errors.append(
                    Warning(
                        ('current site is still `example.com`, Microsoft auth '
                         'might not work'),
                        hint=('Microsoft/Xbox auth uses OAuth, which requires '
                              'a real redirect URI to come back to'),
                        id='microsoft_auth.W002',
                    )
                )
    return errors
