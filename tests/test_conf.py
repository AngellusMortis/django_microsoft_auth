"""Tests for `microsoft_auth.conf` modules without Constance

"""

from unittest.mock import patch

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
        """Tests all the default settings are initialized correctly"""

        from microsoft_auth.conf import config

        for key, setting in DEFAULT_CONFIG["defaults"].items():
            actual_setting = getattr(config, key)
            self.assertEqual(actual_setting, setting[0])

    def test_config_class(self):
        """Tests MICROSOFT_AUTH_CONFIG_CLASS=None"""

        from microsoft_auth.conf import config

        self.assertTrue(isinstance(config, SimpleConfig))
        self.assertFalse(isinstance(config, SimpleTestConfig))

    @override_settings(MICROSOFT_AUTH_CONFIG_CLASS=None)
    def test_config_class_as_none(self):
        """Tests MICROSOFT_AUTH_CONFIG_CLASS=None"""

        from microsoft_auth.conf import config

        self.assertTrue(isinstance(config, SimpleConfig))
        self.assertFalse(isinstance(config, SimpleTestConfig))

    @override_settings(MICROSOFT_AUTH_CONFIG_CLASS="tests.test_conf.test_conf")
    def test_custom_config_class(self):
        """Tests MICROSOFT_AUTH_CONFIG_CLASS set to another class"""
        from microsoft_auth.conf import config

        self.assertTrue(isinstance(config, SimpleTestConfig))

    @override_settings(
        MICROSOFT_AUTH_CONFIG_CLASS="tests.test_conf.no_default_test_conf"
    )
    def test_custom_config_class_with_no_default(self):
        """Tests MICROSOFT_AUTH_CONFIG_CLASS set to another class with no
        add_default_config option"""
        from microsoft_auth.conf import config

        self.assertTrue(isinstance(config, SimpleTestNoDefaultConfig))

    @override_settings(MICROSOFT_AUTH_CONFIG_CLASS="tests.test_conf.SimpleTestConfig")
    def test_custom_config_class_uninstantiated(self):
        """Tests MICROSOFT_AUTH_CONFIG_CLASS set to another class (uninstantiated)"""
        from microsoft_auth.conf import config, init_config

        self.assertTrue(isinstance(config, SimpleTestConfig))

        with patch("tests.test_conf.SimpleTestConfig") as mockClass:
            init_config()
            mockClass.assert_called_once()

    @override_settings(
        MICROSOFT_AUTH_CONFIG_CLASS="tests.test_conf.SimpleTestNoDefaultConfig"
    )
    def test_custom_config_class_with_no_default_uninstantiated(self):
        """
        Tests MICROSOFT_AUTH_CONFIG_CLASS set to another class (uninstantiated) with
        no add_default_config option
        """
        from microsoft_auth.conf import config, init_config

        self.assertTrue(isinstance(config, SimpleTestNoDefaultConfig))

        with patch("tests.test_conf.SimpleTestNoDefaultConfig") as mockClass:
            init_config()
            mockClass.assert_called_once()
