from unittest.mock import Mock, patch

from django.contrib.auth import authenticate, get_user_model
from django.test import RequestFactory, override_settings
from microsoft_auth.models import MicrosoftAccount, XboxLiveAccount
from microsoft_auth.conf import LOGIN_TYPE_XBL

from . import TestCase

CODE = 'test_code'
TOKEN = {'access_token': 'test_token', 'scope': ['test']}
XBOX_TOKEN = {'Token': 'test_token'}
EMAIL = 'some.email@example.com'
FIRST = 'Test'
LAST = 'User'
MISSING_ID = 'some_missing_id'
GAMERTAG = 'Some Gamertag'


@override_settings(
    AUTHENTICATION_BACKENDS=[
        'microsoft_auth.backends.MicrosoftAuthenticationBackend',
        'django.contrib.auth.backends.ModelBackend'
    ],
)
class MicrosoftBackendsTests(TestCase):
    def setUp(self):
        User = get_user_model()

        self.factory = RequestFactory()
        self.request = self.factory.get('/')

        self.linked_account = MicrosoftAccount.objects.create(
            microsoft_id='test_id'
        )
        self.linked_account.user = User.objects.create(username='user1')
        self.linked_account.save()

        self.unlinked_account = MicrosoftAccount.objects.create(
            microsoft_id='missing_id'
        )

        self.unlinked_user = User.objects.create(
            username='user2',
            email='test@example.com',
        )

    def test_authenticate_no_code(self):
        user = authenticate(self.request)

        self.assertIs(user, None)

    @patch('microsoft_auth.backends.MicrosoftClient')
    def test_authenticate_invalid_token(self, mock_client):
        mock_auth = Mock()
        mock_auth.fetch_token.return_value = {}
        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)

        self.assertTrue(mock_auth.fetch_token.called)
        self.assertIs(user, None)

    @patch('microsoft_auth.backends.MicrosoftClient')
    def test_authenticate_invalid_scopes(self, mock_client):
        mock_auth = Mock()
        mock_auth.fetch_token.return_value = TOKEN
        mock_auth.valid_scopes.return_value = False
        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)

        self.assertTrue(mock_auth.fetch_token.called)
        self.assertTrue(mock_auth.valid_scopes.called)
        self.assertIs(user, None)

    @patch('microsoft_auth.backends.MicrosoftClient')
    def test_authenticate_invalid_profile(self, mock_client):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_auth = Mock()
        mock_auth.fetch_token.return_value = TOKEN
        mock_auth.valid_scopes.return_value = True
        mock_auth.get.return_value = mock_response
        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)

        self.assertTrue(mock_auth.fetch_token.called)
        self.assertTrue(mock_auth.valid_scopes.called)
        self.assertIs(user, None)

    @patch('microsoft_auth.backends.MicrosoftClient')
    def test_authenticate_errored_profile(self, mock_client):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'error': None}
        mock_auth = Mock()
        mock_auth.fetch_token.return_value = TOKEN
        mock_auth.valid_scopes.return_value = True
        mock_auth.get.return_value = mock_response
        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)

        self.assertTrue(mock_auth.fetch_token.called)
        self.assertTrue(mock_auth.valid_scopes.called)
        self.assertIs(user, None)

    @patch('microsoft_auth.backends.MicrosoftClient')
    def test_authenticate_existing_user(self, mock_client):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': self.linked_account.microsoft_id,
        }
        mock_auth = Mock()
        mock_auth.fetch_token.return_value = TOKEN
        mock_auth.valid_scopes.return_value = True
        mock_auth.get.return_value = mock_response
        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)

        self.assertIsNot(user, None)
        self.assertEqual(user.id, self.linked_account.user.id)

    @patch('microsoft_auth.backends.MicrosoftClient')
    def test_authenticate_existing_user_missing_user(self, mock_client):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': self.unlinked_account.microsoft_id,
            'userPrincipalName': EMAIL,
        }
        mock_auth = Mock()
        mock_auth.fetch_token.return_value = TOKEN
        mock_auth.valid_scopes.return_value = True
        mock_auth.get.return_value = mock_response
        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)
        self.unlinked_account.refresh_from_db()

        self.assertIsNot(user, None)
        self.assertEqual(user.id, self.unlinked_account.user.id)
        self.assertEqual(EMAIL, self.unlinked_account.user.email)

    @patch('microsoft_auth.backends.MicrosoftClient')
    def test_authenticate_existing_user_no_user_with_name(self, mock_client):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': self.unlinked_account.microsoft_id,
            'userPrincipalName': EMAIL,
            'givenName': FIRST,
            'surname': LAST,
        }
        mock_auth = Mock()
        mock_auth.fetch_token.return_value = TOKEN
        mock_auth.valid_scopes.return_value = True
        mock_auth.get.return_value = mock_response
        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)
        self.unlinked_account.refresh_from_db()

        self.assertIsNot(user, None)
        self.assertEqual(user.id, self.unlinked_account.user.id)
        self.assertEqual(EMAIL, self.unlinked_account.user.email)
        self.assertEqual(FIRST, self.unlinked_account.user.first_name)
        self.assertEqual(LAST, self.unlinked_account.user.last_name)

    @patch('microsoft_auth.backends.MicrosoftClient')
    def test_authenticate_existing_user_unlinked_user(self, mock_client):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': self.unlinked_account.microsoft_id,
            'userPrincipalName': self.unlinked_user.email,
        }
        mock_auth = Mock()
        mock_auth.fetch_token.return_value = TOKEN
        mock_auth.valid_scopes.return_value = True
        mock_auth.get.return_value = mock_response
        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)
        self.unlinked_account.refresh_from_db()

        self.assertIsNot(user, None)
        self.assertEqual(user.id, self.unlinked_account.user.id)
        self.assertEqual(
            self.unlinked_user.id,
            self.unlinked_account.user.id)

    @patch('microsoft_auth.backends.MicrosoftClient')
    def test_authenticate_existing_user_missing_name(self, mock_client):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': self.unlinked_account.microsoft_id,
            'userPrincipalName': self.unlinked_user.email,
            'givenName': FIRST,
            'surname': LAST,
        }
        mock_auth = Mock()
        mock_auth.fetch_token.return_value = TOKEN
        mock_auth.valid_scopes.return_value = True
        mock_auth.get.return_value = mock_response
        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)
        self.unlinked_user.refresh_from_db()

        self.assertIsNot(user, None)
        self.assertEqual(user.id, self.unlinked_user.id)
        self.assertEqual(FIRST, self.unlinked_user.first_name)
        self.assertEqual(LAST, self.unlinked_user.last_name)

    @override_settings(MICROSOFT_AUTH_AUTO_CREATE=False)
    @patch('microsoft_auth.backends.MicrosoftClient')
    def test_authenticate_no_autocreate(self, mock_client):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': MISSING_ID,
        }
        mock_auth = Mock()
        mock_auth.fetch_token.return_value = TOKEN
        mock_auth.valid_scopes.return_value = True
        mock_auth.get.return_value = mock_response
        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)

        self.assertIs(user, None)

    @patch('microsoft_auth.backends.MicrosoftClient')
    def test_authenticate_autocreate(self, mock_client):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': MISSING_ID,
            'userPrincipalName': EMAIL,
        }
        mock_auth = Mock()
        mock_auth.fetch_token.return_value = TOKEN
        mock_auth.valid_scopes.return_value = True
        mock_auth.get.return_value = mock_response
        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)

        self.assertIsNot(user, None)
        self.assertEqual(EMAIL, user.email)
        self.assertEqual(MISSING_ID, user.microsoft_account.microsoft_id)


@override_settings(
    AUTHENTICATION_BACKENDS=[
        'microsoft_auth.backends.MicrosoftAuthenticationBackend',
        'django.contrib.auth.backends.ModelBackend'
    ],
    MICROSOFT_AUTH_LOGIN_TYPE=LOGIN_TYPE_XBL
)
class XboxLiveBackendsTests(TestCase):
    def setUp(self):
        User = get_user_model()

        self.factory = RequestFactory()
        self.request = self.factory.get('/')

        self.linked_account = XboxLiveAccount.objects.create(
            xbox_id='test_id',
            gamertag='test_gamertag',
        )
        self.linked_account.user = User.objects.create(username='user1')
        self.linked_account.save()

    @patch('microsoft_auth.backends.MicrosoftClient')
    def test_authenticate_bad_xbox_token(self, mock_client):
        mock_auth = Mock()
        mock_auth.fetch_token.return_value = TOKEN
        mock_auth.fetch_xbox_token.return_value = {}
        mock_auth.valid_scopes.return_value = True
        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)

        self.assertFalse(mock_auth.get_xbox_profile.called)
        self.assertIs(user, None)

    @patch('microsoft_auth.backends.MicrosoftClient')
    def test_authenticate_existing_user(self, mock_client):
        mock_auth = Mock()
        mock_auth.fetch_token.return_value = TOKEN
        mock_auth.fetch_xbox_token.return_value = XBOX_TOKEN
        mock_auth.valid_scopes.return_value = True
        mock_auth.get_xbox_profile.return_value = {
            'xid': self.linked_account.xbox_id,
            'gtg': self.linked_account.gamertag,
        }
        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)

        self.assertIsNot(user, None)
        self.assertEqual(user.id, self.linked_account.user.id)

    @patch('microsoft_auth.backends.MicrosoftClient')
    def test_authenticate_existing_user_new_gamertag(self, mock_client):
        mock_auth = Mock()
        mock_auth.fetch_token.return_value = TOKEN
        mock_auth.fetch_xbox_token.return_value = XBOX_TOKEN
        mock_auth.valid_scopes.return_value = True
        mock_auth.get_xbox_profile.return_value = {
            'xid': self.linked_account.xbox_id,
            'gtg': GAMERTAG,
        }
        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)
        self.linked_account.refresh_from_db()

        self.assertIsNot(user, None)
        self.assertEqual(user.id, self.linked_account.user.id)
        self.assertEqual(GAMERTAG, self.linked_account.gamertag)

    @override_settings(MICROSOFT_AUTH_AUTO_CREATE=False)
    @patch('microsoft_auth.backends.MicrosoftClient')
    def test_authenticate_no_autocreate(self, mock_client):
        mock_auth = Mock()
        mock_auth.fetch_token.return_value = TOKEN
        mock_auth.fetch_xbox_token.return_value = XBOX_TOKEN
        mock_auth.valid_scopes.return_value = True
        mock_auth.get_xbox_profile.return_value = {
            'xid': MISSING_ID,
            'gtg': GAMERTAG,
        }
        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)

        self.assertIs(user, None)

    @patch('microsoft_auth.backends.MicrosoftClient')
    def test_authenticate_autocreate(self, mock_client):
        mock_auth = Mock()
        mock_auth.fetch_token.return_value = TOKEN
        mock_auth.fetch_xbox_token.return_value = XBOX_TOKEN
        mock_auth.valid_scopes.return_value = True
        mock_auth.get_xbox_profile.return_value = {
            'xid': MISSING_ID,
            'gtg': GAMERTAG,
        }
        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)

        self.assertIsNot(user, None)
        self.assertEqual(GAMERTAG, user.username)
        self.assertEqual(MISSING_ID, user.xbox_live_account.xbox_id)

    @patch('microsoft_auth.backends.MicrosoftClient')
    def test_authenticate_no_sync_username(self, mock_client):
        mock_auth = Mock()
        mock_auth.fetch_token.return_value = TOKEN
        mock_auth.fetch_xbox_token.return_value = XBOX_TOKEN
        mock_auth.valid_scopes.return_value = True
        mock_auth.get_xbox_profile.return_value = {
            'xid': self.linked_account.xbox_id,
            'gtg': GAMERTAG,
        }
        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)
        self.linked_account.refresh_from_db()

        self.assertIsNot(user, None)
        self.assertEqual(user.id, self.linked_account.user.id)
        self.assertNotEqual(GAMERTAG, self.linked_account.user.username)

    @override_settings(MICROSOFT_AUTH_XBL_SYNC_USERNAME=True)
    @patch('microsoft_auth.backends.MicrosoftClient')
    def test_authenticate_sync_username(self, mock_client):
        mock_auth = Mock()
        mock_auth.fetch_token.return_value = TOKEN
        mock_auth.fetch_xbox_token.return_value = XBOX_TOKEN
        mock_auth.valid_scopes.return_value = True
        mock_auth.get_xbox_profile.return_value = {
            'xid': self.linked_account.xbox_id,
            'gtg': GAMERTAG,
        }
        mock_client.return_value = mock_auth

        user = authenticate(self.request, code=CODE)
        self.linked_account.refresh_from_db()
        self.linked_account.user.refresh_from_db()

        self.assertIsNot(user, None)
        self.assertEqual(user.id, self.linked_account.user.id)
        self.assertEqual(GAMERTAG, self.linked_account.user.username)
