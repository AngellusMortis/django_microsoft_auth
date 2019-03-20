from django.test import RequestFactory, override_settings

from microsoft_auth.conf import config
from microsoft_auth.utils import get_scheme

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
