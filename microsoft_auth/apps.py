import base64
import logging

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from django.apps import AppConfig

logger = logging.getLogger("django")


def slurp_file(filename):
    try:
        file = open(filename, "r").read()
    except IOError:
        logger.error("Cannot open or read file: {}".format(filename))
        file = None
    return file


class MicrosoftAuthConfig(AppConfig):
    name = "microsoft_auth"
    verbose_name = "Microsoft Auth"

    def ready(self):
        from . import checks  # noqa
        from .conf import config

        if config.MICROSOFT_AUTH_ASSERTION_CERTIFICATE != "":
            cert_filename = config.MICROSOFT_AUTH_ASSERTION_CERTIFICATE
            cert_pem = slurp_file(cert_filename)

            if cert_pem is None:
                return

            cert_x509 = x509.load_pem_x509_certificate(
                cert_pem.encode(), default_backend()
            )

            thumbprint = cert_x509.fingerprint(hashes.SHA1())  # nosec
            thumbprint_b64 = base64.b64encode(thumbprint).decode()

            config.MICROSOFT_AUTH_ASSERTION_CERTIFICATE_THUMBPRINT = thumbprint_b64

        if config.MICROSOFT_AUTH_ASSERTION_KEY != "":
            key_filename = config.MICROSOFT_AUTH_ASSERTION_KEY

            key_pem = slurp_file(key_filename)
            if key_pem is None:
                return

            key = serialization.load_pem_private_key(
                key_pem.encode(), password=None, backend=default_backend()
            )

            config.MICROSOFT_AUTH_ASSERTION_KEY_CONTENT = key
