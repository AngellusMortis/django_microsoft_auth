from django.apps import apps
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import MicrosoftAccount, XboxLiveAccount

User = get_user_model()

# override admin site template
admin.site.login_template = 'microsoft/admin_login.html'

# djangoql support
extra_base = []
if apps.is_installed('djangoql'):
    from djangoql.admin import DjangoQLSearchMixin

    extra_base = [DjangoQLSearchMixin]

base_admin = extra_base + [admin.ModelAdmin]
base_user_admin = extra_base + [BaseUserAdmin]

# unregister User mode if it is already registered
if admin.site.is_registered(User):
        admin.site.unregister(User)


@admin.register(MicrosoftAccount)
class MicrosoftAccountAdmin(*base_admin):
    readonly_fields = ('microsoft_id',)


class MicrosoftAccountInlineAdmin(admin.StackedInline):
    model = MicrosoftAccount
    readonly_fields = ('microsoft_id',)


@admin.register(XboxLiveAccount)
class XboxLiveAccountAdmin(*base_admin):
    readonly_fields = ('xbox_id', 'gamertag')


class XboxLiveAccountInlineAdmin(admin.StackedInline):
    model = XboxLiveAccount
    readonly_fields = ('xbox_id', 'gamertag')


@admin.register(User)
class UserAdmin(*base_user_admin):
    # adds MicrosoftAccount and XboxLiveAccount foreign keys to User model
    inlines = (
        MicrosoftAccountInlineAdmin,
        XboxLiveAccountInlineAdmin
    )
