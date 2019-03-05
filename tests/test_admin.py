from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from microsoft_auth.models import MicrosoftAccount, XboxLiveAccount


class AdminTests(TestCase):
    def setUp(self):
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

    def test_admin_classes(self):
        """ Admin Classes cannot really be tested with Selenium, so just make
        sure they load """

        self.client.get(reverse("admin:index"))
        self.client.get(
            reverse(
                "admin:auth_user_change", kwargs={"object_id": self.user.id}
            )
        )
        self.client.get(
            reverse(
                "admin:microsoft_auth_microsoftaccount_change",
                kwargs={"object_id": self.microsoft_account.id},
            )
        )
        self.client.get(
            reverse(
                "admin:microsoft_auth_xboxliveaccount_change",
                kwargs={"object_id": self.xbox_account.id},
            )
        )
