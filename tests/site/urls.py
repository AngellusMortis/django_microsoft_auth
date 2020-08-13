from django.conf.urls import include, re_path
from django.contrib import admin

urlpatterns = [
    re_path(r"^accounts/", include("django.contrib.auth.urls")),
    re_path(r"^admin/", admin.site.urls),
    re_path(
        r"^microsoft/",
        include("microsoft_auth.urls", namespace="microsoft_auth"),
    ),
]
