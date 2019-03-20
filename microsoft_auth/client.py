import json
import logging

import jwt
import requests
from django.contrib.sites.models import Site
from django.urls import reverse
from django.utils.functional import cached_property
from jwt.algorithms import RSAAlgorithm
from requests_oauthlib import OAuth2Session

from .conf import LOGIN_TYPE_XBL
from .utils import get_scheme

logger = logging.getLogger("django")


class MicrosoftClient(OAuth2Session):
    """ Simple Microsoft OAuth2 Client to authenticate them

        Extended from Requests-OAuthlib's OAuth2Session class which
            does most of the heavy lifting

        https://requests-oauthlib.readthedocs.io/en/latest/

        Microsoft OAuth documentation can be found at
        https://developer.microsoft.com/en-us/graph/docs/get-started/rest
    """

    _config_url = "https://login.microsoftonline.com/{tenant}/v2.0/.well-known/openid-configuration"  # noqa

    _xbox_authorization_url = "https://login.live.com/oauth20_authorize.srf"
    _xbox_token_url = "https://user.auth.xboxlive.com/user/authenticate"
    _profile_url = "https://xsts.auth.xboxlive.com/xsts/authorize"

    xbox_token = {}

    config = None

    # required OAuth scopes
    SCOPE_XBL = ["XboxLive.signin", "XboxLive.offline_access"]
    SCOPE_MICROSOFT = ["openid", "email"]

    def __init__(self, state=None, request=None, *args, **kwargs):
        from .conf import config

        self.config = config

        extra_scopes = self.config.MICROSOFT_AUTH_EXTRA_SCOPES

        try:
            current_site = Site.objects.get_current(request)
        except Site.DoesNotExist:
            current_site = Site.objects.first()

        domain = current_site.domain
        path = reverse("microsoft_auth:auth-callback")
        scope = " ".join(self.SCOPE_MICROSOFT)

        if self.config.MICROSOFT_AUTH_LOGIN_TYPE == LOGIN_TYPE_XBL:
            scope = " ".join(self.SCOPE_XBL)

        scope = "{} {}".format(scope, extra_scopes).strip()

        scheme = get_scheme(request, self.config)

        super().__init__(
            self.config.MICROSOFT_AUTH_CLIENT_ID,
            scope=scope,
            state=state,
            redirect_uri="{0}://{1}{2}".format(scheme, domain, path),
            *args,
            **kwargs
        )

    @cached_property
    def openid_config(self):
        config_url = self._config_url.format(
            tenant=self.config.MICROSOFT_AUTH_TENANT_ID
        )
        response = self.get(config_url)

        if response.ok:
            return response.json()
        return None

    @cached_property
    def jwks(self):
        response = self.get(self.openid_config["jwks_uri"])

        if response.ok:
            return response.json()["keys"]
        return []

    def get_claims(self):
        if self.token is None:
            return None

        token = self.token["id_token"].encode("utf8")

        kid = jwt.get_unverified_header(token)["kid"]
        public_key = None
        for key in self.jwks:
            if kid == key["kid"]:
                jwk = key
                break

        if jwk is None:
            logger.warn("could not find public key for id_token")
            return None

        public_key = RSAAlgorithm.from_jwk(json.dumps(jwk))

        try:
            claims = jwt.decode(
                token,
                public_key,
                algoithm="RS256",
                audience=self.config.MICROSOFT_AUTH_CLIENT_ID,
            )
        except jwt.PyJWTError as e:
            logger.warn("could verify id_token sig: {}".format(e))
            return None

        return claims

    def authorization_url(self):
        """ Generates Microsoft/Xbox or a Office 365 Authorization URL """

        auth_url = self.openid_config["authorization_endpoint"]
        if self.config.MICROSOFT_AUTH_LOGIN_TYPE == LOGIN_TYPE_XBL:
            auth_url = self._xbox_authorization_url

        return super().authorization_url(auth_url, response_mode="form_post")

    def fetch_token(self, **kwargs):
        """ Fetchs OAuth2 Token with given kwargs"""

        return super().fetch_token(  # pragma: no cover
            self.openid_config["token_endpoint"],
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
                'NotAfter': '2016-10-11T15:01:45.225637Z'
            }
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
