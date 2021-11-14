import base64
import logging

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from django.apps import AppConfig

logger = logging.getLogger("django")


class MicrosoftAuthConfig(AppConfig):
    name = "microsoft_auth"
    verbose_name = "Microsoft Auth"

    def ready(self):
        from . import checks  # noqa
        from .conf import config

        if config.MICROSOFT_AUTH_ASSERTION_CERTIFICATE != "":
            cert = config.MICROSOFT_AUTH_ASSERTION_CERTIFICATE

            try:
                cert_pem = open(cert, "r").read()
            except IOError:
                logger.error("Cannot open or read client certificate: {}".format(cert))

            cert_x509 = x509.load_pem_x509_certificate(
                cert_pem.encode(), default_backend()
            )

            thumbprint = cert_x509.fingerprint(hashes.SHA1())  # nosec
            thumbprint_b64 = base64.b64encode(thumbprint).decode()

            config.MICROSOFT_AUTH_ASSERTION_CERTIFICATE_THUMBPRINT = thumbprint_b64

        if config.MICROSOFT_AUTH_ASSERTION_KEY != "":
            key = config.MICROSOFT_AUTH_ASSERTION_KEY

            try:
                key_pem = open(key, "r").read()
            except IOError:
                logger.error("Cannot open or read client key: {}".format(key))

            key = serialization.load_pem_private_key(
                key_pem.encode(), password=None, backend=default_backend()
            )

            config.MICROSOFT_AUTH_ASSERTION_KEY_CONTENT = key
