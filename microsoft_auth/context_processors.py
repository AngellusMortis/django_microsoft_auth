from django.middleware.csrf import get_token
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from .client import MicrosoftClient
from .conf import config, LOGIN_TYPE_O365, LOGIN_TYPE_XBL


def microsoft(request):
    """ Adds global template variables for microsoft_auth """
    login_type = None
    if config.MICROSOFT_AUTH_LOGIN_TYPE == LOGIN_TYPE_O365:
        login_type = _('Office 365')
    elif config.MICROSOFT_AUTH_LOGIN_TYPE == LOGIN_TYPE_XBL:
        login_type = _('Xbox Live')
    else:
        login_type = _('Microsoft')

    # initialize Microsoft client using CSRF token as state variable
    microsoft = MicrosoftClient(state=get_token(request))
    auth_url = microsoft.authorization_url()[0]
    return {
        'microsoft_login_enabled': config.MICROSOFT_AUTH_LOGIN_ENABLED,
        'microsoft_authorization_url': mark_safe(auth_url),
        'microsoft_login_type_text': login_type}
