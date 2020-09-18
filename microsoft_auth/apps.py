import importlib

from django.apps import AppConfig, apps
from django.core.checks import Critical, Warning, register
from django.db.utils import OperationalError, ProgrammingError
from django.test import RequestFactory

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization

import base64
import logging

class MicrosoftAuthConfig(AppConfig):
    name = "microsoft_auth"
    verbose_name = "Microsoft Auth"

    def ready(self):
        from .conf import config

        if config.MICROSOFT_AUTH_CLIENT_CERTIFICATE != "":
            (cert, key) = config.MICROSOFT_AUTH_CLIENT_CERTIFICATE
            
            try:
                with open(cert, 'r') as file:
                    cert_pem = file.read()
                    cert_x509 = x509.load_pem_x509_certificate(cert_pem.encode(), default_backend())
	               
                    thumbprint = cert_x509.fingerprint(hashes.SHA1())
                    thumbprint_b64 = base64.b64encode(thumbprint).decode()

                    config.MICROSOFT_AUTH_CLIENT_CERTIFICATE_THUMBPRINT = thumbprint_b64

            except (IOError, FileNotFoundError) as x:
               logger.error("Cannot open or read client certificate: {}".format(cert))

            try:
                with open(key, 'r') as file:
                    key_pem = file.read()
                    
                    key = serialization.load_pem_private_key(
                        key_pem.encode(), password=None, backend=default_backend()
                    )

                    config.MICROSOFT_AUTH_CLIENT_CERTIFICATE_KEY = key

            except (IOError, FileNotFoundError) as x:
               logger.error("Cannot open or read client key: {}".format(key))


@register()
def microsoft_auth_validator(app_configs, **kwargs):
    from django.contrib.sites.models import Site
    from .conf import config, HOOK_SETTINGS

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
        if not hasattr(config, "SITE_ID"):
            request = RequestFactory().get("/", HTTP_HOST="example.com")
            current_site = Site.objects.get_current(request)
        else:
            current_site = Site.objects.get_current()
    except Site.DoesNotExist:
        pass
    except (OperationalError, ProgrammingError):
        errors.append(
            Warning(
                "`django.contrib.sites` migrations not ran",
                id="microsoft_auth.W001",
            )
        )
    else:
        if current_site.domain == "example.com":
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
        if config.MICROSOFT_AUTH_CLIENT_SECRET == "" and config.MICROSOFT_AUTH_CLIENT_CERTIFICATE == "":
            errors.append(
                Warning(
                    ("`MICROSOFT_AUTH_CLIENT_SECRET` and `MICROSOFT_AUTH_CLIENT_CERTIFICATE` is not configured"),
                    hint=(
                        "`MICROSOFT_AUTH_LOGIN_ENABLED` is `True`, but "
                        "`MICROSOFT_AUTH_CLIENT_SECRET`and `MICROSOFT_AUTH_CLIENT_CERTIFICATE` is empty. "
                        "Either `MICROSOFT_AUTH_CLIENT_SECRET` or `MICROSOFT_AUTH_CLIENT_CERTIFICATE` must be configured. "
                        "Microsoft auth will be disabled"
                    ),
                    id="microsoft_auth.W004",
                )
            )

        if config.MICROSOFT_AUTH_CLIENT_CERTIFICATE != "":
                (cert, key) = config.MICROSOFT_AUTH_CLIENT_CERTIFICATE
                
                try:
                    with open(cert, 'r') as file:
                        cert_pem = file.read()
                except IOError as x:
                    errors.append(
                        Warning(
                            ("Cannot read client certificate located at: {}".format(cert)),
                            hint=(
                                "`MICROSOFT_AUTH_CLIENT_CERTIFICATE` is set, but the client cert cannot be read."
                                " This can either be because the the file does not exist or django does not have permission to read the file"
                            ),
                            id="microsoft_auth.W005",
                        )
                    )

                try:
                    with open(key, 'r') as file:
                        key_pem = file.read()
                except IOError as x:
                        errors.append(
                            Warning(
                                ("Cannot read client key located at: {}".format(key)),
                                hint=(
                                    "`MICROSOFT_AUTH_CLIENT_CERTIFICATE` is set, but the client key cannot be read."
                                    " This can either be because the the file does not exist or django does not have permission to read the file"
                                ),
                                id="microsoft_auth.W006",
                            )
                        )

    for hook_setting_name in HOOK_SETTINGS:
        hook_setting = getattr(config, hook_setting_name)
        if hook_setting != "":
            parts = hook_setting.rsplit(".", 1)

            if len(parts) != 2:
                errors.append(
                    Critical(
                        ("{} is not a valid python path".format(hook_setting)),
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
                        ("{} does not exist".format(hook_setting)),
                        id="microsoft_auth.E004",
                    )
                )
                return errors

            if not callable(function):
                errors.append(
                    Critical(
                        ("{} is not a callable".format(hook_setting)),
                        id="microsoft_auth.E005",
                    )
                )

    return errors
