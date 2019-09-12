from django.conf.urls import include, url
from django.contrib import admin
from .views import home

urlpatterns = [
    url(r"^home/", home),
    url(r"^accounts/", include("django.contrib.auth.urls")),
    url(r"^admin/", admin.site.urls),
    url(
        r"^microsoft/",
        include("microsoft_auth.urls", namespace="microsoft_auth"),
    ),
]
