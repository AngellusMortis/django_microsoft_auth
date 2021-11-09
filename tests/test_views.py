import json
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.core.signing import dumps
from django.urls import reverse

from microsoft_auth.views import AuthenticateCallbackView

from . import TestCase

TOKEN = "e4675ea8d28a41b8b416fe9ed1fb52b1e4675ea8d28a41b8b416fe9ed1fb52b1"
STATE = dumps({"token": TOKEN}, salt="microsoft_auth")
EXPIRED_STATE = (
    "e4675ea8d28a41b8b416fe9ed1fb52b1e4675ea8d28a41b8b416fe9ed1fb52b1:"
    "1h5CgL:G-QiLZ3hetUPgrdpJlvAfXkZ2RQ"
)
TEST_ERROR = "test"
TEST_ERROR_DESCRIPTION = "some_error"


class ViewsTests(TestCase):
    def setUp(self):
        super().setUp()

        User = get_user_model()

        self.user = User.objects.create(username="test")

    def test_authenticate_callback_bad_method(self):
        response = self.client.get(reverse("microsoft_auth:auth-callback"))

        self.assertEqual(405, response.status_code)

    def test_authenticate_callback_no_params(self):
        response = self.client.post(reverse("microsoft_auth:auth-callback"))
        message = json.loads(response.context["message"])["microsoft_auth"]

        self.assertEqual(400, response.status_code)
        self.assertEqual("bad_state", message["error"])
        self.assertEqual(
            AuthenticateCallbackView.messages["bad_state"],
            message["error_description"],
        )

    def test_authenticate_callback_bad_state_format(self):
        response = self.client.post(
            reverse("microsoft_auth:auth-callback"), {"state": "test"}
        )
        message = json.loads(response.context["message"])["microsoft_auth"]

        self.assertEqual(400, response.status_code)
        self.assertEqual("bad_state", message["error"])
        self.assertEqual(
            AuthenticateCallbackView.messages["bad_state"],
            message["error_description"],
        )

    def test_authenticate_callback_bad_state_length(self):
        response = self.client.post(
            reverse("microsoft_auth:auth-callback"), {"state": "001464"}
        )
        message = json.loads(response.context["message"])["microsoft_auth"]

        self.assertEqual(400, response.status_code)
        self.assertEqual("bad_state", message["error"])
        self.assertEqual(
            AuthenticateCallbackView.messages["bad_state"],
            message["error_description"],
        )

    def test_authenticate_callback_bad_state(self):
        response = self.client.post(
            reverse("microsoft_auth:auth-callback"), {"state": STATE[:-1]}
        )
        message = json.loads(response.context["message"])["microsoft_auth"]

        self.assertEqual(400, response.status_code)
        self.assertEqual("bad_state", message["error"])
        self.assertEqual(
            AuthenticateCallbackView.messages["bad_state"],
            message["error_description"],
        )

    def test_authenticate_callback_bad_state_expired(self):
        response = self.client.post(
            reverse("microsoft_auth:auth-callback"), {"state": EXPIRED_STATE}
        )
        message = json.loads(response.context["message"])["microsoft_auth"]

        self.assertEqual(400, response.status_code)
        self.assertEqual("bad_state", message["error"])
        self.assertEqual(
            AuthenticateCallbackView.messages["bad_state"],
            message["error_description"],
        )

    def test_authenticate_callback_missing_code(self):

        response = self.client.post(
            reverse("microsoft_auth:auth-callback"), {"state": STATE}
        )
        message = json.loads(response.context["message"])["microsoft_auth"]

        self.assertEqual(400, response.status_code)
        self.assertEqual("missing_code", message["error"])
        self.assertEqual(
            AuthenticateCallbackView.messages["missing_code"],
            message["error_description"],
        )

    def test_authenticate_callback_error(self):
        response = self.client.post(
            reverse("microsoft_auth:auth-callback"),
            {
                "state": STATE,
                "error": TEST_ERROR,
                "error_description": TEST_ERROR_DESCRIPTION,
            },
        )
        message = json.loads(response.context["message"])["microsoft_auth"]

        self.assertEqual(400, response.status_code)
        self.assertEqual(TEST_ERROR, message["error"])
        self.assertEqual(TEST_ERROR_DESCRIPTION, message["error_description"])

    def test_authenticate_callback_redirect_error(self):
        response = self.client.post(
            reverse("microsoft_auth:from-auth-redirect"),
            {
                "state": STATE,
                "error": TEST_ERROR,
                "error_description": TEST_ERROR_DESCRIPTION,
            },
        )

        self.assertIn(TEST_ERROR, str(response.content))
        self.assertEqual(400, response.status_code)

    @patch("microsoft_auth.views.authenticate")
    def test_authenticate_callback_fail_auth(self, mock_auth):
        mock_auth.return_value = None

        response = self.client.post(
            reverse("microsoft_auth:auth-callback"),
            {"state": STATE, "code": "test_code"},
        )
        message = json.loads(response.context["message"])["microsoft_auth"]

        self.assertEqual(400, response.status_code)
        self.assertEqual("login_failed", message["error"])
        self.assertEqual(
            AuthenticateCallbackView.messages["login_failed"],
            message["error_description"],
        )

    @patch("microsoft_auth.views.authenticate")
    @patch("microsoft_auth.views.login")
    def test_authenticate_callback_success(self, mock_login, mock_auth):
        mock_auth.return_value = self.user

        response = self.client.post(
            reverse("microsoft_auth:auth-callback"),
            {"state": STATE, "code": "test_code"},
        )
        message = json.loads(response.context["message"])["microsoft_auth"]

        self.assertEqual(200, response.status_code)
        self.assertEqual({}, message)
        mock_login.assert_called_with(response.wsgi_request, self.user)

    @patch("microsoft_auth.views.authenticate")
    @patch("microsoft_auth.views.login")
    def test_authenticate_callback_redirect_success(self, mock_login, mock_auth):
        mock_auth.return_value = self.user

        response = self.client.post(
            reverse("microsoft_auth:from-auth-redirect"),
            {"state": STATE, "code": "test_code"},
        )

        self.assertEqual(302, response.status_code)
        self.assertEqual("/", response.url)
        mock_login.assert_called_with(response.wsgi_request, self.user)

    @patch("microsoft_auth.views.authenticate")
    @patch("microsoft_auth.views.login")
    def test_authenticate_callback_redirect_next_path(self, mock_login, mock_auth):
        mock_auth.return_value = self.user

        next_ = "/next/path"
        state = dumps({"token": TOKEN, "next": next_}, salt="microsoft_auth")
        response = self.client.post(
            reverse("microsoft_auth:from-auth-redirect"),
            {"state": state, "code": "test_code"},
        )

        self.assertEqual(302, response.status_code)
        self.assertEqual(next_, response.url)
        mock_login.assert_called_with(response.wsgi_request, self.user)

    @patch("microsoft_auth.views.authenticate")
    @patch("microsoft_auth.views.login")
    @patch("microsoft_auth.views.get_hook")
    def test_callback_hook(self, mock_get_hook, mock_login, mock_auth):
        def callback(request, context):
            return context

        mock_auth.return_value = self.user

        mock_hook = Mock(side_effect=callback)
        mock_get_hook.return_value = mock_hook

        response = self.client.post(
            reverse("microsoft_auth:auth-callback"),
            {"state": STATE, "code": "test_code"},
        )

        expected_context = {}
        expected_context["base_url"] = response.context["base_url"]
        expected_context["message"] = response.context["message"]

        self.assertIsInstance(expected_context, dict)
        mock_hook.assert_called_with(response.wsgi_request, expected_context)

    def test_to_ms_redirect(self):
        response = self.client.get(
            reverse("microsoft_auth:to-auth-redirect"), fetch_redirect_response=False
        )

        self.assertEqual(302, response.status_code)
