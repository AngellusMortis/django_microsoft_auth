from unittest.mock import Mock, patch

from django.test import RequestFactory, override_settings
from microsoft_auth.conf import LOGIN_TYPE_O365, LOGIN_TYPE_XBL
from microsoft_auth.context_processors import microsoft

from . import TestCase

URL = 'https://example.com'


class ContextProcessorsTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('microsoft_auth.context_processors.MicrosoftClient')
    def test_microsoft_login_enabled(self, mock_client):
        request = self.factory.get('/')
        context = microsoft(request)

        self.assertTrue(context.get('microsoft_login_enabled'))

    @override_settings(MICROSOFT_AUTH_LOGIN_ENABLED=False)
    @patch('microsoft_auth.context_processors.MicrosoftClient')
    def test_microsoft_login_enabled_disabled(self, mock_client):
        request = self.factory.get('/')
        context = microsoft(request)

        self.assertFalse(context.get('microsoft_login_enabled'))

    @patch('microsoft_auth.context_processors.MicrosoftClient')
    @patch('microsoft_auth.context_processors.mark_safe')
    def test_microsoft_authorization_url(self, mock_safe, mock_client):
        mock_client_i = Mock()
        mock_client_i.authorization_url.return_value = [URL]
        mock_client.return_value = mock_client_i
        mock_safe.side_effect = lambda value: value

        request = self.factory.get('/')
        context = microsoft(request)

        self.assertEqual(URL, context.get('microsoft_authorization_url'))

    @patch('microsoft_auth.context_processors.MicrosoftClient')
    def test_microsoft_login_type_text(self, mock_client):

        request = self.factory.get('/')
        context = microsoft(request)

        self.assertEqual('Microsoft', context.get('microsoft_login_type_text'))

    @override_settings(MICROSOFT_AUTH_LOGIN_TYPE=LOGIN_TYPE_O365)
    @patch('microsoft_auth.context_processors.MicrosoftClient')
    def test_microsoft_login_type_text_o365(self, mock_client):

        request = self.factory.get('/')
        context = microsoft(request)

        self.assertEqual('Office 365', context.get('microsoft_login_type_text'))

    @override_settings(MICROSOFT_AUTH_LOGIN_TYPE=LOGIN_TYPE_XBL)
    @patch('microsoft_auth.context_processors.MicrosoftClient')
    def test_microsoft_login_type_text_xbl(self, mock_client):

        request = self.factory.get('/')
        context = microsoft(request)

        self.assertEqual('Xbox Live', context.get('microsoft_login_type_text'))
