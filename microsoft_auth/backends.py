import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from .client import MicrosoftClient
from .conf import config
from .models import MicrosoftAccount, XboxLiveAccount

User = get_user_model()


class MicrosoftAuthenticationBackend(ModelBackend):
    """ Authentication backend to authenticate a user against their Microsoft
        Uses Microsoft's Graph OAuth and XBL servers to authentiate. """

    profile_url = 'https://graph.microsoft.com/v1.0/me'

    def __init__(self, user=None):
        self.logger = logging.getLogger(__name__)
        self.microsoft = MicrosoftClient()

    def authenticate(self, request, code=None):
        """
            Authenticates the user against the Django backend
                using a Microsoft auth code from
            https://login.microsoftonline.com/common/oauth2/v2.0/authorize or
            https://login.live.com/oauth20_authorize.srf

            For more details:
            https://developer.microsoft.com/en-us/graph/docs/get-started/rest
        """

        if code is not None:
            # fetch OAuth token
            token = self.microsoft.fetch_token(code=code)

            # validate permission scopes
            if 'access_token' in token and \
                    self.microsoft.valid_scopes(token['scope']):

                # authenticate Xbox Live user
                if config.MICROSOFT_AUTH_LOGIN_TYPE == 'xbl':
                    xbox_token = self.microsoft.fetch_xbox_token()

                    if 'Token' in xbox_token:
                        response = self.microsoft.get_xbox_profile()
                        return self._get_or_create_xbox_user(response)
                # authenticate Microsoft/Office 365 User
                else:
                    response = self.microsoft.get(self.profile_url)
                    if response.status_code == 200:
                        response = response.json()
                        if 'error' not in response:
                            return self._get_or_create_microsoft_user(response)
        return None

    def _get_or_create_xbox_user(self, data):
        """ Retrieves existing Django user or creates
                a new one from Xbox Live profile data """
        user = None

        try:
            xbox_user = \
                XboxLiveAccount.objects.get(xbox_id=data['xid'])
            # update Gamertag since they can change over time
            if xbox_user.gamertag != data['gtg']:
                xbox_user.gamertag = data['gtg']
                xbox_user.save()
        except XboxLiveAccount.DoesNotExist:
            # create new Xbox Live Account
            xbox_user = XboxLiveAccount(
                xbox_id=data['xid'],
                gamertag=data['gtg'])
            xbox_user.save()

        # verify Xbox Live Account is linked to Django User
        if xbox_user is not None:
            if xbox_user.user is None:
                # create new Django user (Xbox Live endpoint provides no data)
                user = User(username=None)
                user.save()

                xbox_user.user = user
                xbox_user.save()

            user = xbox_user.user
        return user

    def _get_or_create_microsoft_user(self, data):
        """ Retrieves existing Django user or creates
                a new one from Microsoft profile data """
        user = None

        try:
            microsoft_user = \
                MicrosoftAccount.objects.get(microsoft_id=data['id'])
        except MicrosoftAccount.DoesNotExist:
            # create new Microsoft Account
            microsoft_user = MicrosoftAccount(
                microsoft_id=data['id'])
            microsoft_user.save()

        # verify Microsoft Account is linked to Django User
        if microsoft_user is not None:
            if microsoft_user.user is None:
                try:
                    # create new Django user from provided data
                    user = User.objects.get(email=data['userPrincipalName'])

                    if user.first_name == '' and user.last_name == '':
                        user.first_name = data['givenName']
                        user.last_name = data['surname']
                        user.save()
                except User.DoesNotExist:
                    user = User(
                        username=None,
                        first_name=data['givenName'],
                        last_name=data['surname'],
                        email=data['userPrincipalName'])
                    user.save()

                microsoft_user.user = user
                microsoft_user.save()

            user = microsoft_user.user
        return user
