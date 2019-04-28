from unittest.mock import Mock, patch

from django.test import RequestFactory, override_settings

from microsoft_auth.conf import config
from microsoft_auth.utils import get_hook, get_scheme

from . import TestCase


class UtilsTests(TestCase):
    def setUp(self):
        super().setUp()

        self.factory = RequestFactory()
        self.request = self.factory.get("/")

    def test_default(self):
        self.assertEqual(get_scheme(self.request), "https")

    def test_config_param(self):
        self.assertEqual(get_scheme(self.request, config), "https")

    @override_settings(DEBUG=True)
    def test_debug(self):
        self.assertEqual(get_scheme(self.request), "http")

    @override_settings(DEBUG=True)
    def test_debug_no_request(self):
        self.assertEqual(get_scheme(None), "https")

    @override_settings(DEBUG=True)
    def test_debug_forwarded_proto(self):
        self.request.META["HTTP_X_FORWARDED_PROTO"] = "https"

        self.assertEqual(get_scheme(self.request), "https")

    def test_get_hook_invalid(self):
        self.assertIsNone(get_hook("NOT_A_REAL_HOOK"))

    def test_get_hook_valid_default(self):
        self.assertIsNone(get_hook("MICROSOFT_AUTH_AUTHENTICATE_HOOK"))

    @override_settings(
        MICROSOFT_AUTH_AUTHENTICATE_HOOK="tests.test_utils.hook_callback"
    )
    @patch("microsoft_auth.utils.importlib")
    def test_get_hook_valid_not_empty(self, mock_import):
        mock_module = Mock()
        mock_module.hook_callback = Mock()
        mock_import.import_module.return_value = mock_module

        function = get_hook("MICROSOFT_AUTH_AUTHENTICATE_HOOK")

        self.assertEqual(function, mock_module.hook_callback)
