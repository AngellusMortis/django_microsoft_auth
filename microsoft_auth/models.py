from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


class MicrosoftAccount(models.Model):
    microsoft_id = models.CharField(_('microsoft account id'), max_length=32)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, null=True,
        related_name='microsoft_account',
    )

    def __str__(self):
        return self.microsoft_id


class XboxLiveAccount(models.Model):
    xbox_id = models.CharField(_('xbox user id'), max_length=32, unique=True)
    gamertag = models.CharField(_('xbox live gamertag'), max_length=16)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, null=True,
        related_name='xbox_live_account',
    )

    def __str__(self):
        return self.gamertag
