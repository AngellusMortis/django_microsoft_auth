from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from .client import MicrosoftClient
from .conf import LOGIN_TYPE_XBL
from .models import MicrosoftAccount, XboxLiveAccount

User = get_user_model()


class MicrosoftAuthenticationBackend(ModelBackend):
    """ Authentication backend to authenticate a user against their Microsoft
        Uses Microsoft's Graph OAuth and XBL servers to authentiate. """

    config = None
    microsoft = None
    profile_url = 'https://graph.microsoft.com/v1.0/me'

    def __init__(self, user=None):
        from .conf import config
        self.config = config
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

        user = None
        if code is not None:
            # fetch OAuth token
            token = self.microsoft.fetch_token(code=code)

            # validate permission scopes
            if 'access_token' in token and \
                    self.microsoft.valid_scopes(token['scope']):
                user = self._authenticate_user()

        return user

    def _authenticate_user(self):
        if self.config.MICROSOFT_AUTH_LOGIN_TYPE == LOGIN_TYPE_XBL:
            return self._authenticate_xbox_user()
        else:
            return self._authenticate_microsoft_user()

    def _authenticate_xbox_user(self):
        xbox_token = self.microsoft.fetch_xbox_token()

        if 'Token' in xbox_token:
            response = self.microsoft.get_xbox_profile()
            return self._get_user_from_xbox(response)
        return None

    def _authenticate_microsoft_user(self):
        response = self.microsoft.get(self.profile_url)
        if response.status_code == 200:
            response = response.json()
            if 'error' not in response:
                return self._get_user_from_microsoft(response)
        return None

    def _get_user_from_xbox(self, data):
        """ Retrieves existing Django user or creates
            a new one from Xbox Live profile data """
        user = None
        xbox_user = self._get_xbox_user(data)

        if xbox_user is not None:
            self._verify_xbox_user(xbox_user)

            user = xbox_user.user

            if self.config.MICROSOFT_AUTH_XBL_SYNC_USERNAME and \
                    user.username != xbox_user.gamertag:
                user.username = xbox_user.gamertag
                user.save()

        return user

    def _get_xbox_user(self, data):
        xbox_user = None

        try:
            xbox_user = XboxLiveAccount.objects.get(xbox_id=data['xid'])
            # update Gamertag since they can change over time
            if xbox_user.gamertag != data['gtg']:
                xbox_user.gamertag = data['gtg']
                xbox_user.save()
        except XboxLiveAccount.DoesNotExist:
            if self.config.MICROSOFT_AUTH_AUTO_CREATE:
                # create new Xbox Live Account
                xbox_user = XboxLiveAccount(
                    xbox_id=data['xid'],
                    gamertag=data['gtg'])
                xbox_user.save()

        return xbox_user

    def _verify_xbox_user(self, xbox_user):
        if xbox_user.user is None:
            user = User(username=xbox_user.gamertag)
            user.save()

            xbox_user.user = user
            xbox_user.save()

    def _get_user_from_microsoft(self, data):
        """ Retrieves existing Django user or creates
            a new one from Xbox Live profile data """
        user = None
        microsoft_user = self._get_microsoft_user(data)

        if microsoft_user is not None:
            self._verify_microsoft_user(microsoft_user, data)

            user = microsoft_user.user

        return user

    def _get_microsoft_user(self, data):
        microsoft_user = None

        try:
            microsoft_user = \
                MicrosoftAccount.objects.get(microsoft_id=data['id'])
        except MicrosoftAccount.DoesNotExist:
            if self.config.MICROSOFT_AUTH_AUTO_CREATE:
                # create new Microsoft Account
                microsoft_user = MicrosoftAccount(
                    microsoft_id=data['id'])
                microsoft_user.save()

        return microsoft_user

    def _verify_microsoft_user(self, microsoft_user, data):
        if microsoft_user.user is None:
            try:
                # create new Django user from provided data
                user = User.objects.get(email=data['userPrincipalName'])

                if user.first_name == '' and user.last_name == '':
                    user.first_name = data.get('givenName', '')
                    user.last_name = data.get('surname', '')
                    user.save()
            except User.DoesNotExist:
                user = User(
                    username=data['id'],
                    first_name=data.get('givenName', ''),
                    last_name=data.get('surname', ''),
                    email=data['userPrincipalName'])
                user.save()

            microsoft_user.user = user
            microsoft_user.save()
