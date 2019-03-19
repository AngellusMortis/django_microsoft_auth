from unittest.mock import Mock, patch

from django.contrib.auth import authenticate, get_user_model
from django.db.utils import IntegrityError
from django.test import RequestFactory, TestCase, override_settings

from microsoft_auth.conf import LOGIN_TYPE_XBL
from microsoft_auth.models import MicrosoftAccount, XboxLiveAccount

CODE = "test_code"
TOKEN = {"access_token": "test_token", "scope": ["test"]}
XBOX_TOKEN = {"Token": "test_token"}
EMAIL = "some.email@example.com"
EMAIL2 = "some.email2@example.com"
FIRST = "Test"
LAST = "User"
MISSING_ID = "some_missing_id"
GAMERTAG = "Some Gamertag"


@override_settings(
    AUTHENTICATION_BACKENDS=[
        "microsoft_auth.backends.MicrosoftAuthenticationBackend",
        "django.contrib.auth.backends.ModelBackend",
    ]
)
class MicrosoftBackendsTests(TestCase):
    def setUp(self):
        User = get_user_model()

        self.factory = RequestFactory()
        self.request = self.factory.get("/")

        self.linked_account = MicrosoftAccount.objects.create(
            microsoft_id="test_id"
        )
        self.linked_account.user = User.objects.create(
            username="user1", email=EMAIL2
        )
        self.linked_account.save()

        self.unlinked_account = MicrosoftAccount.objects.create(
            microsoft_id="missing_id"
        )

        self.unlinked_user = User.objects.create(
            username="user2", email="test@example.com"
        )

    def test_authenticate_no_code(self):
        user = authenticate(self.request)

        self.assertIs(user, None)

    @patch("microsoft_auth.backends.MicrosoftClient")
    def test_authenticate_invalid_token(self, mock_client):
        mock_auth = Mock()
        mock_auth.fetch_token.return_value = {}

        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)

        self.assertTrue(mock_auth.fetch_token.called)
        self.assertIs(user, None)

    @patch("microsoft_auth.backends.MicrosoftClient")
    def test_authenticate_invalid_scopes(self, mock_client):
        mock_auth = Mock()
        mock_auth.fetch_token.return_value = TOKEN
        mock_auth.valid_scopes.return_value = False

        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)

        self.assertTrue(mock_auth.fetch_token.called)
        self.assertTrue(mock_auth.valid_scopes.called)
        self.assertIs(user, None)

    @patch("microsoft_auth.backends.MicrosoftClient")
    def test_authenticate_invalid_profile(self, mock_client):
        mock_auth = Mock()
        mock_auth.fetch_token.return_value = TOKEN
        mock_auth.valid_scopes.return_value = True
        mock_auth.get_claims.return_value = None

        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)

        self.assertTrue(mock_auth.fetch_token.called)
        self.assertTrue(mock_auth.valid_scopes.called)
        self.assertIs(user, None)

    @patch("microsoft_auth.backends.MicrosoftClient")
    def test_authenticate_errored_profile(self, mock_client):
        mock_auth = Mock()
        mock_auth.fetch_token.return_value = TOKEN
        mock_auth.valid_scopes.return_value = True
        mock_auth.get_claims.return_value = None

        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)

        self.assertTrue(mock_auth.fetch_token.called)
        self.assertTrue(mock_auth.valid_scopes.called)
        self.assertIs(user, None)

    @patch("microsoft_auth.backends.MicrosoftClient")
    def test_authenticate_existing_user(self, mock_client):
        mock_auth = Mock()
        mock_auth.fetch_token.return_value = TOKEN
        mock_auth.valid_scopes.return_value = True
        mock_auth.get_claims.return_value = {
            "sub": self.linked_account.microsoft_id
        }

        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)

        self.assertIsNot(user, None)
        self.assertEqual(user.id, self.linked_account.user.id)

    @patch("microsoft_auth.backends.MicrosoftClient")
    def test_authenticate_existing_user_missing_user(self, mock_client):
        mock_auth = Mock()
        mock_auth.fetch_token.return_value = TOKEN
        mock_auth.valid_scopes.return_value = True
        mock_auth.get_claims.return_value = {
            "sub": self.unlinked_account.microsoft_id,
            "email": EMAIL,
            "name": "{} {}".format(FIRST, LAST),
            "preferred_username": EMAIL,
        }

        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)
        self.unlinked_account.refresh_from_db()

        self.assertIsNot(user, None)
        self.assertEqual(user.id, self.unlinked_account.user.id)
        self.assertEqual(EMAIL, self.unlinked_account.user.email)

    @patch("microsoft_auth.backends.MicrosoftClient")
    def test_authenticate_existing_user_no_user_with_name(self, mock_client):
        mock_auth = Mock()
        mock_auth.fetch_token.return_value = TOKEN
        mock_auth.valid_scopes.return_value = True
        mock_auth.get_claims.return_value = {
            "sub": self.unlinked_account.microsoft_id,
            "email": EMAIL,
            "name": "{} {}".format(FIRST, LAST),
            "preferred_username": EMAIL,
        }

        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)
        self.unlinked_account.refresh_from_db()

        self.assertIsNot(user, None)
        self.assertEqual(user.id, self.unlinked_account.user.id)
        self.assertEqual(EMAIL, self.unlinked_account.user.email)
        self.assertEqual(FIRST, self.unlinked_account.user.first_name)
        self.assertEqual(LAST, self.unlinked_account.user.last_name)

    @patch("microsoft_auth.backends.MicrosoftClient")
    def test_authenticate_existing_user_unlinked_user(self, mock_client):
        mock_auth = Mock()
        mock_auth.fetch_token.return_value = TOKEN
        mock_auth.valid_scopes.return_value = True
        mock_auth.get_claims.return_value = {
            "sub": self.unlinked_account.microsoft_id,
            "email": self.unlinked_user.email,
            "name": "{} {}".format(FIRST, LAST),
            "preferred_username": EMAIL,
        }

        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)
        self.unlinked_account.refresh_from_db()

        self.assertIsNot(user, None)
        self.assertEqual(user.id, self.unlinked_account.user.id)
        self.assertEqual(self.unlinked_user.id, self.unlinked_account.user.id)

    @patch("microsoft_auth.backends.MicrosoftClient")
    def test_authenticate_existing_user_unlinked_user_no_autofill(
        self, mock_client
    ):
        expected_first_name = "Test"
        expected_last_name = "User"

        self.unlinked_user.first_name = expected_first_name
        self.unlinked_user.last_name = expected_last_name
        self.unlinked_user.save()

        mock_auth = Mock()
        mock_auth.fetch_token.return_value = TOKEN
        mock_auth.valid_scopes.return_value = True
        mock_auth.get_claims.return_value = {
            "sub": self.unlinked_account.microsoft_id,
            "email": self.unlinked_user.email,
            "name": "{} {}".format(FIRST, LAST),
            "preferred_username": EMAIL,
        }

        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)
        self.unlinked_account.refresh_from_db()

        self.assertIsNot(user, None)
        self.assertEqual(user.id, self.unlinked_account.user.id)
        self.assertEqual(self.unlinked_user.id, self.unlinked_account.user.id)
        self.assertEqual(expected_first_name, self.unlinked_user.first_name)
        self.assertEqual(expected_last_name, self.unlinked_user.last_name)

    @patch("microsoft_auth.backends.MicrosoftClient")
    def test_authenticate_existing_user_missing_name(self, mock_client):
        mock_auth = Mock()
        mock_auth.fetch_token.return_value = TOKEN
        mock_auth.valid_scopes.return_value = True
        mock_auth.get_claims.return_value = {
            "sub": self.unlinked_account.microsoft_id,
            "email": self.unlinked_user.email,
            "name": "{} {}".format(FIRST, LAST),
            "preferred_username": EMAIL,
        }

        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)
        self.unlinked_user.refresh_from_db()

        self.assertIsNot(user, None)
        self.assertEqual(user.id, self.unlinked_user.id)
        self.assertEqual(FIRST, self.unlinked_user.first_name)
        self.assertEqual(LAST, self.unlinked_user.last_name)

    @override_settings(MICROSOFT_AUTH_AUTO_CREATE=False)
    @patch("microsoft_auth.backends.MicrosoftClient")
    def test_authenticate_no_autocreate(self, mock_client):
        mock_auth = Mock()
        mock_auth.fetch_token.return_value = TOKEN
        mock_auth.valid_scopes.return_value = True
        mock_auth.get_claims.return_value = {"sub": MISSING_ID}

        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)

        self.assertIs(user, None)

    @patch("microsoft_auth.backends.MicrosoftClient")
    def test_authenticate_autocreate(self, mock_client):
        mock_auth = Mock()
        mock_auth.fetch_token.return_value = TOKEN
        mock_auth.valid_scopes.return_value = True
        mock_auth.get_claims.return_value = {
            "sub": MISSING_ID,
            "email": EMAIL,
            "name": "{} {}".format(FIRST, LAST),
            "preferred_username": EMAIL,
        }

        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)

        self.assertIsNot(user, None)
        self.assertEqual(EMAIL, user.email)
        self.assertEqual(MISSING_ID, user.microsoft_account.microsoft_id)

    @patch("microsoft_auth.backends.MicrosoftClient")
    def test_authenticate_existing_linked_default(self, mock_client):
        mock_auth = Mock()
        mock_auth.fetch_token.return_value = TOKEN
        mock_auth.valid_scopes.return_value = True
        mock_auth.get_claims.return_value = {
            "sub": MISSING_ID,
            "email": EMAIL2,
            "name": "{} {}".format(FIRST, LAST),
            "preferred_username": EMAIL,
        }

        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)

        self.assertIsNone(user)

    @override_settings(MICROSOFT_AUTH_AUTO_REPLACE_ACCOUNTS=True)
    @patch("microsoft_auth.backends.MicrosoftClient")
    def test_authenticate_existing_linked_replace(self, mock_client):
        mock_auth = Mock()
        mock_auth.fetch_token.return_value = TOKEN
        mock_auth.valid_scopes.return_value = True
        mock_auth.get_claims.return_value = {
            "sub": MISSING_ID,
            "email": EMAIL2,
            "name": "{} {}".format(FIRST, LAST),
            "preferred_username": EMAIL,
        }

        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)
        self.linked_account.refresh_from_db()

        self.assertIsNot(user, None)
        self.assertEqual(EMAIL2, user.email)
        self.assertEqual(MISSING_ID, user.microsoft_account.microsoft_id)
        self.assertIsNone(self.linked_account.user)


@override_settings(
    AUTHENTICATION_BACKENDS=[
        "microsoft_auth.backends.MicrosoftAuthenticationBackend",
        "django.contrib.auth.backends.ModelBackend",
    ],
    MICROSOFT_AUTH_LOGIN_TYPE=LOGIN_TYPE_XBL,
)
class XboxLiveBackendsTests(TestCase):
    def setUp(self):
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
