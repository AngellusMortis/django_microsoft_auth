"""Tests for `microsoft_auth.conf` modules without Constance

"""

from django.test import override_settings

from microsoft_auth.conf import DEFAULT_CONFIG, SimpleConfig

from . import TransactionTestCase


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

    @override_settings(MICROSOFT_AUTH_CONFIG_CLASS="tests.test_conf.test_conf")
    def test_custom_config_class(self):
        """ Tests MICROSOFT_AUTH_CONFIG_CLASS set to another class """
        from microsoft_auth.conf import config

        self.assertTrue(isinstance(config, SimpleTestConfig))

    @override_settings(
        MICROSOFT_AUTH_CONFIG_CLASS="tests.test_conf.no_default_test_conf"
    )
    def test_custom_config_class_with_no_default(self):
        """ Tests MICROSOFT_AUTH_CONFIG_CLASS set to another class with no
            add_default_config option """
        from microsoft_auth.conf import config

        self.assertTrue(isinstance(config, SimpleTestNoDefaultConfig))
