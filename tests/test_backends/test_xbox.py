from unittest.mock import Mock, patch

from django.contrib.auth import authenticate, get_user_model
from django.test import RequestFactory, override_settings

from microsoft_auth.conf import LOGIN_TYPE_XBL
from microsoft_auth.models import XboxLiveAccount

from .. import TestCase

CODE = "test_code"
TOKEN = {"access_token": "test_token", "scope": ["test"]}
XBOX_TOKEN = {"Token": "test_token"}
LAST = "User"
MISSING_ID = "some_missing_id"
GAMERTAG = "Some Gamertag"


@override_settings(
    AUTHENTICATION_BACKENDS=[
        "microsoft_auth.backends.MicrosoftAuthenticationBackend",
        "django.contrib.auth.backends.ModelBackend",
    ],
    MICROSOFT_AUTH_LOGIN_TYPE=LOGIN_TYPE_XBL,
)
class XboxLiveBackendsTests(TestCase):
    def setUp(self):
        super().setUp()

        User = get_user_model()

        self.factory = RequestFactory()
        self.request = self.factory.get("/")

        self.linked_account = XboxLiveAccount.objects.create(
            xbox_id="test_id", gamertag="test_gamertag"
        )
        self.linked_account.user = User.objects.create(username="user1")
        self.linked_account.save()

    @patch("microsoft_auth.backends.MicrosoftClient")
    def test_authenticate_bad_xbox_token(self, mock_client):
        mock_auth = Mock()
        mock_auth.fetch_token.return_value = TOKEN
        mock_auth.fetch_xbox_token.return_value = {}
        mock_auth.valid_scopes.return_value = True

        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)

        self.assertFalse(mock_auth.get_xbox_profile.called)
        self.assertIs(user, None)

    @patch("microsoft_auth.backends.MicrosoftClient")
    def test_authenticate_existing_user(self, mock_client):
        mock_auth = Mock()
        mock_auth.fetch_token.return_value = TOKEN
        mock_auth.fetch_xbox_token.return_value = XBOX_TOKEN
        mock_auth.valid_scopes.return_value = True
        mock_auth.get_xbox_profile.return_value = {
            "xid": self.linked_account.xbox_id,
            "gtg": self.linked_account.gamertag,
        }

        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)

        self.assertIsNot(user, None)
        self.assertEqual(user.id, self.linked_account.user.id)

    @patch("microsoft_auth.backends.MicrosoftClient")
    def test_authenticate_existing_user_new_gamertag(self, mock_client):
        mock_auth = Mock()
        mock_auth.fetch_token.return_value = TOKEN
        mock_auth.fetch_xbox_token.return_value = XBOX_TOKEN
        mock_auth.valid_scopes.return_value = True
        mock_auth.get_xbox_profile.return_value = {
            "xid": self.linked_account.xbox_id,
            "gtg": GAMERTAG,
        }

        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)
        self.linked_account.refresh_from_db()

        self.assertIsNot(user, None)
        self.assertEqual(user.id, self.linked_account.user.id)
        self.assertEqual(GAMERTAG, self.linked_account.gamertag)

    @override_settings(MICROSOFT_AUTH_AUTO_CREATE=False)
    @patch("microsoft_auth.backends.MicrosoftClient")
    def test_authenticate_no_autocreate(self, mock_client):
        mock_auth = Mock()
        mock_auth.fetch_token.return_value = TOKEN
        mock_auth.fetch_xbox_token.return_value = XBOX_TOKEN
        mock_auth.valid_scopes.return_value = True
        mock_auth.get_xbox_profile.return_value = {
            "xid": MISSING_ID,
            "gtg": GAMERTAG,
        }

        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)

        self.assertIs(user, None)

    @patch("microsoft_auth.backends.MicrosoftClient")
    def test_authenticate_autocreate(self, mock_client):
        mock_auth = Mock()
        mock_auth.fetch_token.return_value = TOKEN
        mock_auth.fetch_xbox_token.return_value = XBOX_TOKEN
        mock_auth.valid_scopes.return_value = True
        mock_auth.get_xbox_profile.return_value = {
            "xid": MISSING_ID,
            "gtg": GAMERTAG,
        }

        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)

        self.assertIsNot(user, None)
        self.assertEqual(GAMERTAG, user.username)
        self.assertEqual(MISSING_ID, user.xbox_live_account.xbox_id)

    @patch("microsoft_auth.backends.MicrosoftClient")
    def test_authenticate_no_sync_username(self, mock_client):
        mock_auth = Mock()
        mock_auth.fetch_token.return_value = TOKEN
        mock_auth.fetch_xbox_token.return_value = XBOX_TOKEN
        mock_auth.valid_scopes.return_value = True
        mock_auth.get_xbox_profile.return_value = {
            "xid": self.linked_account.xbox_id,
            "gtg": GAMERTAG,
        }

        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)
        self.linked_account.refresh_from_db()

        self.assertIsNot(user, None)
        self.assertEqual(user.id, self.linked_account.user.id)
        self.assertNotEqual(GAMERTAG, self.linked_account.user.username)

    @override_settings(MICROSOFT_AUTH_XBL_SYNC_USERNAME=True)
    @patch("microsoft_auth.backends.MicrosoftClient")
    def test_authenticate_sync_username(self, mock_client):
        mock_auth = Mock()
        mock_auth.fetch_token.return_value = TOKEN
        mock_auth.fetch_xbox_token.return_value = XBOX_TOKEN
        mock_auth.valid_scopes.return_value = True
        mock_auth.get_xbox_profile.return_value = {
            "xid": self.linked_account.xbox_id,
            "gtg": GAMERTAG,
        }

        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)
        self.linked_account.refresh_from_db()
        self.linked_account.user.refresh_from_db()

        self.assertIsNot(user, None)
        self.assertEqual(user.id, self.linked_account.user.id)
        self.assertEqual(GAMERTAG, self.linked_account.user.username)

    @override_settings(
        MICROSOFT_AUTH_AUTHENTICATE_HOOK="tests.test_backends.test_xbox.hook_callback"  # noqa
    )
    @patch("microsoft_auth.backends.MicrosoftClient")
    @patch("microsoft_auth.backends.importlib")
    def test_authenticate_hook(self, mock_import, mock_client):
        mock_module = Mock()
        mock_module.hook_callback = Mock()
        mock_import.import_module.return_value = mock_module

        mock_auth = Mock()
        mock_auth.fetch_token.return_value = TOKEN
        mock_auth.fetch_xbox_token.return_value = XBOX_TOKEN
        mock_auth.valid_scopes.return_value = True
        mock_auth.get_xbox_profile.return_value = {
            "xid": MISSING_ID,
            "gtg": GAMERTAG,
        }
        mock_auth.xbox_token = XBOX_TOKEN

        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)

        mock_module.hook_callback.assert_called_with(user, XBOX_TOKEN)
