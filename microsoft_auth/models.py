from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _


class NullableUsernameUser(AbstractUser):
    def __str__(self):
        return str(super(NullableUsernameUser, self).__str__())

    def save(self, *args, **kwargs):
        if self.username == '':
            self.username = None
        return super().save(*args, **kwargs)

    class Meta:
        abstract = True
NullableUsernameUser._meta.get_field('username').null = True  # noqa


class MicrosoftAccount(models.Model):
    microsoft_id = models.CharField(_('microsoft account id'), max_length=32)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.microsoft_id


class XboxLiveAccount(models.Model):
    xbox_id = models.CharField(_('xbox user id'), max_length=32, unique=True)
    gamertag = models.CharField(_('xbox live gamertag'), max_length=16)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.gamertag
