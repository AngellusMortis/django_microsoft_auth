import importlib

from django.apps import AppConfig, apps
from django.core.checks import Critical, Warning, register
from django.db.utils import OperationalError
from django.test import RequestFactory


class MicrosoftAuthConfig(AppConfig):
    name = "microsoft_auth"
    verbose_name = "Microsoft Auth"


@register()
def microsoft_auth_validator(app_configs, **kwargs):
    from django.contrib.sites.models import Site
    from .conf import config

    errors = []

    if apps.is_installed("microsoft_auth") and not apps.is_installed(
        "django.contrib.sites"
    ):

        errors.append(
            Critical(
                "`django.contrib.sites` is not installed",
                hint=(
                    "`microsoft_auth` requires `django.contrib.sites` "
                    "to be installed and configured"
                ),
                id="microsoft_auth.E001",
            )
        )

    try:
        request = RequestFactory().get("/", HTTP_HOST="example.com")
        Site.objects.get_current(request)
    except Site.DoesNotExist:
        pass
    except OperationalError:
        errors.append(
            Warning(
                "`django.contrib.sites` migrations not ran",
                id="microsoft_auth.W001",
            )
        )
    else:
        errors.append(
            Warning(
                (
                    "`example.com` is still a valid site, Microsoft "
                    "auth might not work"
                ),
                hint=(
                    "Microsoft/Xbox auth uses OAuth, which requires "
                    "a real redirect URI to come back to"
                ),
                id="microsoft_auth.W002",
            )
        )

    if config.MICROSOFT_AUTH_LOGIN_ENABLED:  # pragma: no branch
        if config.MICROSOFT_AUTH_CLIENT_ID == "":
            errors.append(
                Warning(
                    ("`MICROSOFT_AUTH_CLIENT_ID` is not configured"),
                    hint=(
                        "`MICROSOFT_AUTH_LOGIN_ENABLED` is `True`, but "
                        "`MICROSOFT_AUTH_CLIENT_ID` is empty. Microsoft "
                        "auth will be disabled"
                    ),
                    id="microsoft_auth.W003",
                )
            )
        if config.MICROSOFT_AUTH_CLIENT_SECRET == "":
            errors.append(
                Warning(
                    ("`MICROSOFT_AUTH_CLIENT_SECRET` is not configured"),
                    hint=(
                        "`MICROSOFT_AUTH_LOGIN_ENABLED` is `True`, but "
                        "`MICROSOFT_AUTH_CLIENT_SECRET` is empty. Microsoft "
                        "auth will be disabled"
                    ),
                    id="microsoft_auth.W004",
                )
            )

    if config.MICROSOFT_AUTH_AUTHENTICATE_HOOK != "":
        parts = config.MICROSOFT_AUTH_AUTHENTICATE_HOOK.rsplit(".", 1)

        if len(parts) != 2:
            errors.append(
                Critical(
                    (
                        "{} is not a valid python path".format(
                            config.MICROSOFT_AUTH_AUTHENTICATE_HOOK
                        )
                    ),
                    id="microsoft_auth.E002",
                )
            )
            return errors

        module_path, function_name = parts[0], parts[1]
        try:
            module = importlib.import_module(module_path)
        except ImportError:
            errors.append(
                Critical(
                    ("{} is not a valid module".format(module_path)),
                    id="microsoft_auth.E003",
                )
            )
            return errors

        try:
            function = getattr(module, function_name)
        except AttributeError:
            errors.append(
                Critical(
                    (
                        "{} does not exist".format(
                            config.MICROSOFT_AUTH_AUTHENTICATE_HOOK
                        )
                    ),
                    id="microsoft_auth.E004",
                )
            )
            return errors

        if not callable(function):
            errors.append(
                Critical(
                    (
                        "{} is not a callable".format(
                            config.MICROSOFT_AUTH_AUTHENTICATE_HOOK
                        )
                    ),
                    id="microsoft_auth.E005",
                )
            )

    return errors
