import json
import urllib.parse
from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlparse

from django.contrib.sites.models import Site
from django.test import RequestFactory, override_settings

from microsoft_auth.client import MicrosoftClient
from microsoft_auth.conf import LOGIN_TYPE_XBL

from . import TestCase

STATE = "test_state"
CLIENT_ID = "test_client_id"
REDIRECT_URI = "https://testserver/microsoft/auth-callback/"
ACCESS_TOKEN = "test_access_token"
XBOX_TOKEN = "test_xbox_token"
XBOX_PROFILE = "test_profile"


@override_settings(SITE_ID=1)
class ClientTests(TestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()

    def setUp(self):
        super().setUp()

        self.factory = RequestFactory()

    def _get_auth_url(self, base_url, scopes=MicrosoftClient.SCOPE_MICROSOFT):
        args = {
            "response_type": "code",
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "scope": " ".join(scopes),
            "state": STATE,
            "response_mode": "form_post",
        }
        return (base_url + "?" + urllib.parse.urlencode(args), STATE)

    def _assert_auth_url(self, expected, actual):
        # parse urls
        e_url = urlparse(expected[0])
        e_qs = parse_qs(e_url.query)
        a_url = urlparse(actual[0])
        a_qs = parse_qs(a_url.query)

        # assert url
        self.assertEqual(e_url.scheme, a_url.scheme)
        self.assertEqual(e_url.path, a_url.path)
        self.assertEqual(e_url.netloc, a_url.netloc)
        self.assertEqual(len(e_qs.items()), len(a_qs.items()))
        for key, value in e_qs.items():
            self.assertEqual(value, a_qs[key])

        # assert state
        self.assertEqual(expected[1], actual[1])

    def test_scope(self):
        expected_scopes = " ".join(MicrosoftClient.SCOPE_MICROSOFT)

        auth_client = MicrosoftClient()
        self.assertEqual(expected_scopes, auth_client.scope)

    @override_settings(MICROSOFT_AUTH_LOGIN_TYPE=LOGIN_TYPE_XBL)
    def test_xbox_scopes(self):
        expected_scopes = " ".join(MicrosoftClient.SCOPE_XBL)

        auth_client = MicrosoftClient()
        self.assertEqual(expected_scopes, auth_client.scope)

    def test_state(self):
        auth_client = MicrosoftClient(state=STATE)
        self.assertEqual(STATE, auth_client.state)

    def test_redirect_uri(self):
        auth_client = MicrosoftClient()
        self.assertEqual(REDIRECT_URI, auth_client.redirect_uri)

    @override_settings(MICROSOFT_AUTH_CLIENT_ID=CLIENT_ID)
    def test_authorization_url(self):
        auth_client = MicrosoftClient(state=STATE)

        base_url = auth_client.openid_config["authorization_endpoint"]
        expected_auth_url = self._get_auth_url(base_url)

        self._assert_auth_url(
            expected_auth_url, auth_client.authorization_url()
        )

    @override_settings(
        MICROSOFT_AUTH_CLIENT_ID=CLIENT_ID,
        MICROSOFT_AUTH_LOGIN_TYPE=LOGIN_TYPE_XBL,
    )
    def test_authorization_url_with_xbl(self):
        base_url = MicrosoftClient._xbox_authorization_url
        expected_auth_url = self._get_auth_url(
            base_url, scopes=MicrosoftClient.SCOPE_XBL
        )

        auth_client = MicrosoftClient(state=STATE)
        self._assert_auth_url(
            expected_auth_url, auth_client.authorization_url()
        )

    @patch("microsoft_auth.client.requests")
    def test_fetch_xbox_token(self, mock_requests):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = XBOX_TOKEN
        mock_requests.post.return_value = mock_response

        auth_client = MicrosoftClient()
        auth_client.token = {"access_token": ACCESS_TOKEN}
        xbox_token = auth_client.fetch_xbox_token()

        self.assertEqual(XBOX_TOKEN, xbox_token)
        self.assertEqual(XBOX_TOKEN, auth_client.xbox_token)

    @patch("microsoft_auth.client.requests")
    def test_fetch_xbox_token_params(self, mock_requests):
        expected_headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
        }
        expected_data = json.dumps(
            {
                "RelyingParty": "http://auth.xboxlive.com",
                "TokenType": "JWT",
                "Properties": {
                    "AuthMethod": "RPS",
                    "SiteName": "user.auth.xboxlive.com",
                    "RpsTicket": "d={}".format(ACCESS_TOKEN),
                },
            }
        )

        auth_client = MicrosoftClient()
        auth_client.token = {"access_token": ACCESS_TOKEN}
        auth_client.fetch_xbox_token()

        mock_requests.post.assert_called_with(
            MicrosoftClient._xbox_token_url,
            data=expected_data,
            headers=expected_headers,
        )

    @patch("microsoft_auth.client.requests")
    def test_fetch_xbox_token_bad_response(self, mock_requests):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_requests.post.return_value = mock_response

        auth_client = MicrosoftClient()
        auth_client.token = {"access_token": ACCESS_TOKEN}
        xbox_token = auth_client.fetch_xbox_token()

        self.assertEqual({}, xbox_token)
        self.assertEqual({}, auth_client.xbox_token)

    @patch("microsoft_auth.client.requests")
    def test_get_xbox_profile(self, mock_requests):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "DisplayClaims": {"xui": [XBOX_PROFILE]}
        }
        mock_requests.post.return_value = mock_response

        auth_client = MicrosoftClient()
        auth_client.xbox_token = {"Token": XBOX_TOKEN}
        xbox_profile = auth_client.get_xbox_profile()

        self.assertEqual(XBOX_PROFILE, xbox_profile)

    @patch("microsoft_auth.client.requests")
    def test_get_xbox_profile_params(self, mock_requests):
        expected_headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
        }
        expected_data = json.dumps(
            {
                "RelyingParty": "http://xboxlive.com",
                "TokenType": "JWT",
                "Properties": {
                    "UserTokens": [XBOX_TOKEN],
                    "SandboxId": "RETAIL",
                },
            }
        )

        auth_client = MicrosoftClient()
        auth_client.xbox_token = {"Token": XBOX_TOKEN}
        auth_client.get_xbox_profile()

        mock_requests.post.assert_called_with(
            MicrosoftClient._profile_url,
            data=expected_data,
            headers=expected_headers,
        )

    @patch("microsoft_auth.client.requests")
    def test_get_xbox_profile_bad_response(self, mock_requests):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_requests.post.return_value = mock_response

        auth_client = MicrosoftClient()
        auth_client.xbox_token = {"Token": XBOX_TOKEN}
        xbox_profile = auth_client.get_xbox_profile()

        self.assertEqual({}, xbox_profile)

    def test_get_xbox_profile_no_token(self):
        auth_client = MicrosoftClient()
        xbox_profile = auth_client.get_xbox_profile()

        self.assertEqual({}, xbox_profile)

    def test_valid_scopes(self):
        scopes = MicrosoftClient.SCOPE_MICROSOFT

        auth_client = MicrosoftClient()
        self.assertTrue(auth_client.valid_scopes(scopes))

    def test_valid_scopes_invalid(self):
        scopes = ["fake"]

        auth_client = MicrosoftClient()
        self.assertFalse(auth_client.valid_scopes(scopes))

    @override_settings(MICROSOFT_AUTH_LOGIN_TYPE=LOGIN_TYPE_XBL)
    def test_valid_scopes_xbox(self):
        scopes = MicrosoftClient.SCOPE_XBL

        auth_client = MicrosoftClient()
        self.assertTrue(auth_client.valid_scopes(scopes))

    @override_settings(
        SITE_ID=None, ALLOWED_HOSTS=["example.com", "testserver"]
    )
    def test_alternative_site(self):
        self.assertEqual(Site.objects.get(pk=1).domain, "testserver")

        Site.objects.create(domain="example.com", name="example.com")

        request = self.factory.get("/", HTTP_HOST="example.com")

        self.assertEqual(
            Site.objects.get_current(request).domain, "example.com"
        )

        client = MicrosoftClient(request=request)

        self.assertIn("example.com", client.authorization_url()[0])
