from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from microsoft_auth.views import AuthenticateCallbackView
import json

from . import TestCase

CSRF_TOKEN = 'e4675ea8d28a41b8b416fe9ed1fb52b1e4675ea8d28a41b8b416fe9ed1fb52b1'
TEST_ERROR = 'test'
TEST_ERROR_DESCRIPTION = 'some_error'


class ViewsTests(TestCase):
    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create(username='test')

    def test_authenticate_callback_bad_method(self):
        response = self.client.get(reverse('microsoft:auth-callback'))

        self.assertEqual(405, response.status_code)

    def test_authenticate_callback_no_params(self):
        response = self.client.post(reverse('microsoft:auth-callback'))
        message = json.loads(response.context['message'])

        self.assertEqual(400, response.status_code)
        self.assertEqual('bad_state', message['error'])
        self.assertEqual(
            AuthenticateCallbackView.messages['bad_state'],
            message['error_description'])

    @patch('microsoft_auth.views._compare_salted_tokens')
    def test_authenticate_callback_bad_csrf_format(self, mock_compare):
        response = self.client.post(
            reverse('microsoft:auth-callback'),
            {'state': 'test'}
        )
        message = json.loads(response.context['message'])

        self.assertFalse(mock_compare.called)
        self.assertEqual(400, response.status_code)
        self.assertEqual('bad_state', message['error'])
        self.assertEqual(
            AuthenticateCallbackView.messages['bad_state'],
            message['error_description'])

    @patch('microsoft_auth.views._compare_salted_tokens')
    def test_authenticate_callback_bad_csrf_length(self, mock_compare):
        response = self.client.post(
            reverse('microsoft:auth-callback'),
            {'state': '001464'}
        )
        message = json.loads(response.context['message'])

        self.assertFalse(mock_compare.called)
        self.assertEqual(400, response.status_code)
        self.assertEqual('bad_state', message['error'])
        self.assertEqual(
            AuthenticateCallbackView.messages['bad_state'],
            message['error_description'])

    @patch('microsoft_auth.views._compare_salted_tokens')
    def test_authenticate_callback_bad_csrf(self, mock_compare):
        mock_compare.return_value = False

        response = self.client.post(
            reverse('microsoft:auth-callback'),
            {'state': CSRF_TOKEN}
        )
        message = json.loads(response.context['message'])

        self.assertTrue(mock_compare.called)
        self.assertEqual(400, response.status_code)
        self.assertEqual('bad_state', message['error'])
        self.assertEqual(
            AuthenticateCallbackView.messages['bad_state'],
            message['error_description'])

    @patch('microsoft_auth.views._compare_salted_tokens')
    def test_authenticate_callback_missing_code(self, mock_compare):
        mock_compare.return_value = True

        response = self.client.post(
            reverse('microsoft:auth-callback'),
            {'state': CSRF_TOKEN}
        )
        message = json.loads(response.context['message'])

        self.assertTrue(mock_compare.called)
        self.assertEqual(400, response.status_code)
        self.assertEqual('missing_code', message['error'])
        self.assertEqual(
            AuthenticateCallbackView.messages['missing_code'],
            message['error_description'])

    @patch('microsoft_auth.views._compare_salted_tokens')
    def test_authenticate_callback_error(self, mock_compare):
        mock_compare.return_value = True

        response = self.client.post(
            reverse('microsoft:auth-callback'),
            {
                'state': CSRF_TOKEN,
                'error': TEST_ERROR,
                'error_description': TEST_ERROR_DESCRIPTION,
            }
        )
        message = json.loads(response.context['message'])

        self.assertTrue(mock_compare.called)
        self.assertEqual(400, response.status_code)
        self.assertEqual(TEST_ERROR, message['error'])
        self.assertEqual(
            TEST_ERROR_DESCRIPTION,
            message['error_description'])

    @patch('microsoft_auth.views.authenticate')
    @patch('microsoft_auth.views._compare_salted_tokens')
    def test_authenticate_callback_fail_auth(self, mock_compare, mock_auth):
        mock_compare.return_value = True
        mock_auth.return_value = None

        response = self.client.post(
            reverse('microsoft:auth-callback'),
            {
                'state': CSRF_TOKEN,
                'code': 'test_code'
            }
        )
        message = json.loads(response.context['message'])

        self.assertTrue(mock_compare.called)
        self.assertEqual(400, response.status_code)
        self.assertEqual('login_failed', message['error'])
        self.assertEqual(
            AuthenticateCallbackView.messages['login_failed'],
            message['error_description'])

    @patch('microsoft_auth.views.authenticate')
    @patch('microsoft_auth.views._compare_salted_tokens')
    @patch('microsoft_auth.views.login')
    def test_authenticate_callback_success(self, mock_login,
                                           mock_compare, mock_auth):
        mock_compare.return_value = True
        mock_auth.return_value = self.user

        response = self.client.post(
            reverse('microsoft:auth-callback'),
            {
                'state': CSRF_TOKEN,
                'code': 'test_code'
            }
        )
        message = json.loads(response.context['message'])

        self.assertTrue(mock_compare.called)
        self.assertEqual(200, response.status_code)
        self.assertEqual({}, message)
        mock_login.assert_called_with(
            response.wsgi_request,
            self.user
        )
