"""Tests for `microsoft_auth.conf` modules

Note: This file must be last in test runner as Constance does not get
cleaned correctly afterwards
"""

from unittest.mock import patch

import pytest
from django.core.management import call_command
from django.test import modify_settings

from microsoft_auth.conf import DEFAULT_CONFIG

from . import TestCase
from .test_conf import ConfTests

pytest.importorskip("constance")


@modify_settings(
    INSTALLED_APPS={"prepend": ["constance", "constance.backends.database"]}
)
class ConstanceTests(TestCase):
    def test_constance_admin(self):
        self.client.get("/admin/constance/config/")

    def test_config_constance_not_found(self):
        from microsoft_auth.conf import config, init_config

        init_config()

        with self.assertRaises(AttributeError):
            config.NOT_A_REAL_SETTING


@modify_settings(
    INSTALLED_APPS={"prepend": ["constance", "constance.backends.database"]}
)
class ConstanceConfTests(ConfTests):
    def setUp(self):
        super().setUp()

        call_command("migrate", "database", "zero")
        call_command("migrate", "database", "0001")


@patch("constance.base.settings.CONFIG", DEFAULT_CONFIG["defaults"])
@patch("constance.base.settings.CONFIG_FIELDSETS", DEFAULT_CONFIG["fieldsets"])
class ConstanceWithDefaultsConfTests(ConstanceConfTests):
    pass
