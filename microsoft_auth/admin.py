from django.apps import apps
from django.contrib import admin
from django.contrib.auth import get_user_model

from .conf import LOGIN_TYPE_MA, LOGIN_TYPE_XBL, config
from .models import MicrosoftAccount, XboxLiveAccount

__all__ = [
    "MicrosoftAccountAdmin",
    "MicrosoftAccountInlineAdmin",
    "UserAdmin",
    "XboxLiveAccountAdmin",
    "XboxLiveAccountInlineAdmin",
]

User = get_user_model()

# override admin site template
admin.site.login_template = "microsoft/admin_login.html"

# djangoql support
extra_base = []
if apps.is_installed("djangoql"):  # pragma: no branch
    from djangoql.admin import DjangoQLSearchMixin

    extra_base = [DjangoQLSearchMixin]

base_admin = extra_base + [admin.ModelAdmin]


class MicrosoftAccountAdmin(*base_admin):
    readonly_fields = ("microsoft_id",)


class MicrosoftAccountInlineAdmin(admin.StackedInline):
    model = MicrosoftAccount
    readonly_fields = ("microsoft_id",)


class XboxLiveAccountAdmin(*base_admin):
    readonly_fields = ("xbox_id", "gamertag")


class XboxLiveAccountInlineAdmin(admin.StackedInline):
    model = XboxLiveAccount
    readonly_fields = ("xbox_id", "gamertag")


def _register_admins():
    _do_both = config.MICROSOFT_AUTH_REGISTER_INACTIVE_ADMIN
    _login_type = config.MICROSOFT_AUTH_LOGIN_TYPE

    if admin.site.is_registered(MicrosoftAccount):
        admin.site.unregister(MicrosoftAccount)

    if admin.site.is_registered(XboxLiveAccount):
        admin.site.unregister(XboxLiveAccount)

    if _do_both or _login_type == LOGIN_TYPE_MA:
        admin.site.register(MicrosoftAccount, MicrosoftAccountAdmin)
    if _do_both or _login_type == LOGIN_TYPE_XBL:
        admin.site.register(XboxLiveAccount, XboxLiveAccountAdmin)


def _get_inlines():
    _do_both = config.MICROSOFT_AUTH_REGISTER_INACTIVE_ADMIN
    _login_type = config.MICROSOFT_AUTH_LOGIN_TYPE
    inlines = []

    if _do_both or _login_type == LOGIN_TYPE_MA:
        inlines.append(MicrosoftAccountInlineAdmin)
    if _do_both or _login_type == LOGIN_TYPE_XBL:
        inlines.append(XboxLiveAccountInlineAdmin)

    return inlines


try:
    UserAdmin = admin.site._registry[User]
except KeyError:
    from django.contrib.auth.admin import UserAdmin

UserAdmin.inlines.extend(_get_inlines())

_register_admins()
