from .conf import config

urlpatterns = []

if config.MICROSOFT_AUTH_LOGIN_ENABLED:
    from django.conf.urls import url
    from . import views

    urlpatterns = [
        url(r'^auth-callback/$',
            views.AuthenticateCallbackView.as_view(),
            name='auth-callback'),
    ]
