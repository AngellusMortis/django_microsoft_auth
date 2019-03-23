import io
import sys

from django.core.management import call_command
from django.core.management.base import SystemCheckError
from django.test import modify_settings, override_settings

from . import TransactionTestCase


def hook_callback(user, token):
    pass


@override_settings(
    MICROSOFT_AUTH_CLIENT_ID="test-client-id",
    MICROSOFT_AUTH_CLIENT_SECRET="test-client-secret",
)
class ChecksTests(TransactionTestCase):
    def setUp(self):
        super().setUp()

        self.captured = io.StringIO()
        sys.stdout = self.captured
        sys.stderr = self.captured

    def tearDown(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def test_all_pass(self):
        call_command("check")

    @modify_settings(INSTALLED_APPS={"remove": "django.contrib.sites"})
    def test_sites_install_fails(self):
        with self.assertRaises(SystemCheckError) as exc:
            call_command("check")

        self.assertIn("microsoft_auth.E001", str(exc.exception))

    def test_sites_migrations_fails(self):
        call_command("migrate", "sites", "zero")
        call_command("check")
        call_command("migrate", "sites", "0001")

        self.assertIn("microsoft_auth.W001", self.captured.getvalue())

    def test_sites_default_name_fails(self):
        self.site.domain = "example.com"
        self.site.save()

        call_command("check")

        self.assertIn("microsoft_auth.W002", self.captured.getvalue())

    @override_settings(MICROSOFT_AUTH_CLIENT_ID="")
    def test_config_client_id_fails(self):
        call_command("check")

        self.assertIn("microsoft_auth.W003", self.captured.getvalue())

    @override_settings(MICROSOFT_AUTH_CLIENT_SECRET="")
    def test_config_client_secret_fails(self):
        call_command("check")

        self.assertIn("microsoft_auth.W004", self.captured.getvalue())

    @override_settings(MICROSOFT_AUTH_AUTHENTICATE_HOOK="bogus")
    def test_config_hook_invalid_path(self):
        with self.assertRaises(SystemCheckError) as exc:
            call_command("check")

        self.assertIn("microsoft_auth.E002", str(exc.exception))

    @override_settings(MICROSOFT_AUTH_AUTHENTICATE_HOOK="bogus.function")
    def test_config_hook_invalid_module(self):
        with self.assertRaises(SystemCheckError) as exc:
            call_command("check")

        self.assertIn("microsoft_auth.E003", str(exc.exception))

    @override_settings(MICROSOFT_AUTH_AUTHENTICATE_HOOK="microsoft_auth.bogus")
    def test_config_hook_invalid_function_path(self):
        with self.assertRaises(SystemCheckError) as exc:
            call_command("check")

        self.assertIn("microsoft_auth.E004", str(exc.exception))

    @override_settings(MICROSOFT_AUTH_AUTHENTICATE_HOOK="microsoft_auth.conf")
    def test_config_hook_invalid_function(self):
        with self.assertRaises(SystemCheckError) as exc:
            call_command("check")

        self.assertIn("microsoft_auth.E005", str(exc.exception))

    @override_settings(
        MICROSOFT_AUTH_AUTHENTICATE_HOOK="tests.test_apps.hook_callback"
    )
    def test_config_hook_valid(self):
        call_command("check")

        self.assertNotIn("microsoft_auth", self.captured.getvalue())
