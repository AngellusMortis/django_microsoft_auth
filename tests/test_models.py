from microsoft_auth.models import MicrosoftAccount, XboxLiveAccount

from . import TestCase

USER_ID = 'test_user_id'


class ModelsTests(TestCase):
    def test_microsoft_account_str(self):
        a = MicrosoftAccount(microsoft_id=USER_ID)
        a.save()

        self.assertEqual(USER_ID, str(a))

    def test_xbox_account_str(self):
        a = XboxLiveAccount(gamertag=USER_ID)
        a.save()

        self.assertEqual(USER_ID, str(a))
