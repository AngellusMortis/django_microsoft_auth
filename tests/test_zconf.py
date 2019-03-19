"""Tests for `microsoft_auth.conf` modules

Note: This file must be last in test runner as Constance does not get
cleaned correctly afterwards
"""

from django.core.management import call_command
from django.test import TransactionTestCase, modify_settings, override_settings

from microsoft_auth.conf import DEFAULT_CONFIG, SimpleConfig

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class SimpleTestConfig(SimpleConfig):
    pass


class SimpleTestNoDefaultConfig:
    pass


no_default_test_conf = SimpleTestNoDefaultConfig()
test_conf = SimpleTestConfig()


class ConfTests(TransactionTestCase):
    def test_default_settings(self):
        """ Tests all the default settings are initialized correctly """

        from microsoft_auth.conf import config

        for key, setting in DEFAULT_CONFIG["defaults"].items():
            actual_setting = getattr(config, key)
            self.assertEqual(actual_setting, setting[0])

    def test_config_class(self):
        """ Tests MICROSOFT_AUTH_CONFIG_CLASS=None """

        from microsoft_auth.conf import config

        self.assertTrue(isinstance(config, SimpleConfig))
        self.assertFalse(isinstance(config, SimpleTestConfig))

    @override_settings(MICROSOFT_AUTH_CONFIG_CLASS=None)
    def test_config_class_as_none(self):
        """ Tests MICROSOFT_AUTH_CONFIG_CLASS=None """

        from microsoft_auth.conf import config

        self.assertTrue(isinstance(config, SimpleConfig))
        self.assertFalse(isinstance(config, SimpleTestConfig))

    @override_settings(
        MICROSOFT_AUTH_CONFIG_CLASS="tests.test_zconf.test_conf"
    )
    def test_custom_config_class(self):
        """ Tests MICROSOFT_AUTH_CONFIG_CLASS set to another class """
        from microsoft_auth.conf import config

        self.assertTrue(isinstance(config, SimpleTestConfig))

    @override_settings(
        MICROSOFT_AUTH_CONFIG_CLASS="tests.test_zconf.no_default_test_conf"
    )
    def test_custom_config_class_with_no_default(self):
        """ Tests MICROSOFT_AUTH_CONFIG_CLASS set to another class with no
            add_default_config option """
        from microsoft_auth.conf import config

        self.assertTrue(isinstance(config, SimpleTestNoDefaultConfig))


@modify_settings(
    INSTALLED_APPS={"prepend": ["constance", "constance.backends.database"]}
)
class ConstanceConfTests(ConfTests):
    def setUp(self):
        super(ConstanceConfTests, self).setUp()
        call_command("migrate", "database", "zero")
        call_command("migrate", "database", "0001")


@patch("constance.base.settings.CONFIG", DEFAULT_CONFIG["defaults"])
@patch("constance.base.settings.CONFIG_FIELDSETS", DEFAULT_CONFIG["fieldsets"])
class ConstanceWithDefaultsConfTests(ConstanceConfTests):
    pass
