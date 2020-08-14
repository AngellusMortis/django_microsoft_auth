from .conf import config

app_name = "microsoft_auth"

urlpatterns = []

if config.MICROSOFT_AUTH_LOGIN_ENABLED:  # pragma: no branch
    try:
        from django.urls import re_path
    except ImportError:
        from django.conf.urls import url as re_path

    from . import views

    urlpatterns = [
        re_path(
            r"^auth-callback/$",
            views.AuthenticateCallbackView.as_view(),
            name="auth-callback",
        )
    ]
