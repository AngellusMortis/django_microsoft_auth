import json

import requests
from django.contrib.sites.models import Site
from django.urls import reverse
from requests_oauthlib import OAuth2Session
from .conf import LOGIN_TYPE_XBL


class MicrosoftClient(OAuth2Session):
    """ Simple Microsoft OAuth2 Client to authenticate them

        Extended from Requests-OAuthlib's OAuth2Session class which
            does most of the heavy lifting

        https://requests-oauthlib.readthedocs.io/en/latest/

        Microsoft OAuth documentation can be found at
        https://developer.microsoft.com/en-us/graph/docs/get-started/rest
    """

    _authorization_url = (
        "https://login.microsoftonline.com/TENANT/oauth2/v2.0/authorize"
    )
    _token_url = "https://login.microsoftonline.com/TENANT/oauth2/v2.0/token"

    _xbox_authorization_url = "https://login.live.com/oauth20_authorize.srf"
    _xbox_token_url = "https://user.auth.xboxlive.com/user/authenticate"
    _profile_url = "https://xsts.auth.xboxlive.com/xsts/authorize"

    xbox_token = {}

    config = None

    # required OAuth scopes
    SCOPE_XBL = ["XboxLive.signin", "XboxLive.offline_access"]
    SCOPE_MICROSOFT = ["User.Read"]

    def __init__(self, state=None, request=None, *args, **kwargs):
        from .conf import config

        self.config = config

        domain = Site.objects.get_current().domain
        path = reverse("microsoft_auth:auth-callback")
        scope = self.config.MICROSOFT_AUTH_SCOPE

        if self.config.MICROSOFT_AUTH_LOGIN_TYPE == LOGIN_TYPE_XBL:
            scope = " ".join(self.SCOPE_XBL)

        scheme = "https"
        if config.DEBUG and request is not None:
            scheme = request.scheme

        super().__init__(
            self.config.MICROSOFT_AUTH_CLIENT_ID,
            scope=scope,
            state=state,
            redirect_uri="{0}://{1}{2}".format(scheme, domain, path),
            *args,
            **kwargs
        )

    def authorization_url(self):
        """ Generates Microsoft/Xbox or a Office 365 Authorization URL """
        auth_url = self._authorization_url
        tenant = self.config.MICROSOFT_AUTH_TENANT_ID
        auth_url = auth_url.replace('TENANT', tenant)
        if self.config.MICROSOFT_AUTH_LOGIN_TYPE == LOGIN_TYPE_XBL:
            auth_url = self._xbox_authorization_url

        return super().authorization_url(auth_url, response_mode="form_post")

    def fetch_token(self, **kwargs):
        """ Fetchs OAuth2 Token with given kwargs"""
        tenant = self.config.MICROSOFT_AUTH_TENANT_ID
        url = self._token_url.replace('TENANT', tenant)
        return super().fetch_token(
            url,
            client_secret=self.config.MICROSOFT_AUTH_CLIENT_SECRET,
            **kwargs
        )

    def fetch_xbox_token(self):
        """ Fetches Xbox Live Auth token.

            token must contain a valid access_token
                - retrieved from fetch_token

            Reversed engineered from existing Github repos,
                no "official" API docs from Microsoft

            Response will be similar to
            {
                'Token': 'token',
                'IssueInstant': '2016-09-27T15:01:45.225637Z',
                'DisplayClaims': {'xui': [{'uhs': '###################'}]},
                'NotAfter': '2016-10-11T15:01:45.225637Z'}
            """

        # Content-type MUST be json for Xbox Live
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
        }
        params = {
            "RelyingParty": "http://auth.xboxlive.com",
            "TokenType": "JWT",
            "Properties": {
                "AuthMethod": "RPS",
                "SiteName": "user.auth.xboxlive.com",
                "RpsTicket": "d={}".format(self.token["access_token"]),
            },
        }
        response = requests.post(
            self._xbox_token_url, data=json.dumps(params), headers=headers
        )

        if response.status_code == 200:
            self.xbox_token = response.json()

        return self.xbox_token

    def get_xbox_profile(self):
        """
            Fetches the Xbox Live user profile from Xbox servers

            xbox_token must contain a valid Xbox Live token
                - retrieved from fetch_xbox_token

            Reversed engineered from existing Github repos,
                no "official" API docs from Microsoft

            Response will be similar to
            {
                'NotAfter': '2016-09-28T07:19:21.9608601Z',
                'DisplayClaims': {
                    'xui': [
                        {
                            'agg': 'Adult',
                            'uhs': '###################',
                            'usr': '###',
                            'xid': '################',
                            'prv': '### ### ###...',
                            'gtg': 'Gamertag'}]},
                'IssueInstant': '2016-09-27T15:19:21.9608601Z',
                'Token': 'token'}
        """

        if "Token" in self.xbox_token:
            # Content-type MUST be json for Xbox Live
            headers = {
                "Content-type": "application/json",
                "Accept": "application/json",
            }
            params = {
                "RelyingParty": "http://xboxlive.com",
                "TokenType": "JWT",
                "Properties": {
                    "UserTokens": [self.xbox_token["Token"]],
                    "SandboxId": "RETAIL",
                },
            }
            response = requests.post(
                self._profile_url, data=json.dumps(params), headers=headers
            )

            if response.status_code == 200:
                return response.json()["DisplayClaims"]["xui"][0]
        return {}

    def valid_scopes(self, scopes):
        """ Validates response scopes based on MICROSOFT_AUTH_LOGIN_TYPE """
        scopes = set(scopes)
        required_scopes = None
        if self.config.MICROSOFT_AUTH_LOGIN_TYPE == LOGIN_TYPE_XBL:
            required_scopes = set(self.SCOPE_XBL)
        else:
            required_scopes = set(self.SCOPE_MICROSOFT)

        # verify all require_scopes are in scopes
        return required_scopes <= scopes
