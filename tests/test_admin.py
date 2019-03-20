from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse

from microsoft_auth.admin import _register_admins
from microsoft_auth.conf import LOGIN_TYPE_MA, LOGIN_TYPE_XBL
from microsoft_auth.models import MicrosoftAccount, XboxLiveAccount

from . import TestCase


class AdminTests(TestCase):
    def setUp(self):
        super().setUp()

        User = get_user_model()

        self.user = User.objects.create_superuser(
            "test", "test@example.com", "password1"
        )
        self.microsoft_account = MicrosoftAccount.objects.create(
            microsoft_id="test", user=self.user
        )
        self.xbox_account = XboxLiveAccount.objects.create(
            xbox_id="test", gamertag="test", user=self.user
        )

        self.client.force_login(self.user)

    @override_settings(
        MICROSOFT_AUTH_LOGIN_TYPE=LOGIN_TYPE_MA,
        MICROSOFT_AUTH_REGISTER_INACTIVE_ADMIN=False,
    )
    def test_admin_classes_microsoft_auth(self):
        """ Verify only Microsoft Auth classes are injected """

        _register_admins()

        self.client.get(reverse("admin:index"))
        self.client.get(
            reverse("admin:auth_user_change", args=(self.user.id,))
        )

        self.client.get(
            reverse(
                "admin:microsoft_auth_microsoftaccount_change",
                args=(self.microsoft_account.id,),
            )
        )

    @override_settings(
        MICROSOFT_AUTH_LOGIN_TYPE=LOGIN_TYPE_XBL,
        MICROSOFT_AUTH_REGISTER_INACTIVE_ADMIN=False,
    )
    def test_admin_classes_xbox(self):
        """ Verify only Xbox classes are injected """

        _register_admins()

        self.client.get(reverse("admin:index"))
        self.client.get(
            reverse("admin:auth_user_change", args=(self.user.id,))
        )

        self.client.get(
            reverse(
                "admin:microsoft_auth_xboxliveaccount_change",
                args=(self.xbox_account.id,),
            )
        )

    @override_settings(MICROSOFT_AUTH_REGISTER_INACTIVE_ADMIN=True)
    def test_admin_classes_both(self):
        """ Verify both admin classes are injected """

        _register_admins()

        self.client.get(reverse("admin:index"))
        self.client.get(
            reverse("admin:auth_user_change", args=(self.user.id,))
        )

        self.client.get(
            reverse(
                "admin:microsoft_auth_microsoftaccount_change",
                args=(self.microsoft_account.id,),
            )
        )
        self.client.get(
            reverse(
                "admin:microsoft_auth_xboxliveaccount_change",
                args=(self.xbox_account.id,),
            )
        )
