import logging

from django.contrib.sites.models import Site
from django.core.signing import Signer
from django.middleware.csrf import get_token
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from .client import MicrosoftClient
from .conf import LOGIN_TYPE_XBL, config
from .utils import get_scheme

logger = logging.getLogger("django")


def microsoft(request):
    """ Adds global template variables for microsoft_auth """
    login_type = None
    if config.MICROSOFT_AUTH_LOGIN_TYPE == LOGIN_TYPE_XBL:
        login_type = _("Xbox Live")
    else:
        login_type = _("Microsoft")

    if config.DEBUG:  # pragma: no branch
        expected_domain = Site.objects.get_current().domain
        current_domain = request.get_host()
        if expected_domain != current_domain:  # pragma: no branch
            logger.warning(
                "\nWARNING:\nThe domain configured for the sites framework "
                "does not match the domain you are accessing Django with. "
                "Microsoft authentication may not work.\n"
            )

        do_warning = get_scheme(
            request
        ) == "http" and not current_domain.startswith("localhost")
        if do_warning:  # pragma: no branch
            logger.warning(
                "\nWARNING:\nYou are not using HTTPS. Microsoft "
                "authentication only works over HTTPS unless the hostname for "
                "your `redirect_uri` is `localhost`\n"
            )

    # initialize Microsoft client using CSRF token as state variable
    signer = Signer()
    state = signer.sign(get_token(request))
    microsoft = MicrosoftClient(state=state, request=request)
    auth_url = microsoft.authorization_url()[0]
    return {
        "microsoft_login_enabled": config.MICROSOFT_AUTH_LOGIN_ENABLED,
        "microsoft_authorization_url": mark_safe(auth_url),
        "microsoft_login_type_text": login_type,
    }
