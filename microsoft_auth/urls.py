from django.urls import path

from .conf import config

app_name = "microsoft_auth"

urlpatterns = []

if config.MICROSOFT_AUTH_LOGIN_ENABLED:  # pragma: no branch
    from . import views

    urlpatterns = [
        path(
            "auth-callback/",
            views.AuthenticateCallbackView.as_view(),
            name="auth-callback",
        ),
        path(
            "from-auth-redirect/",
            views.AuthenticateCallbackRedirect.as_view(),
            name="from-auth-redirect",
        ),
        path(
            "to-auth-redirect/",
            views.to_ms_redirect,
            name="to-auth-redirect",
        )
    ]
