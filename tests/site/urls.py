from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r"^accounts/", include("django.contrib.auth.urls")),
    url(r"^admin/", admin.site.urls),
    url(
        r"^microsoft/",
        include("microsoft_auth.urls", namespace="microsoft_auth"),
    ),
]
