from django.contrib import admin

try:
    from django.urls import include, re_path
except ImportError:
    from django.conf.urls import include
    from django.conf.urls import url as re_path

urlpatterns = [
    re_path(r"^accounts/", include("django.contrib.auth.urls")),
    re_path(r"^admin/", admin.site.urls),
    re_path(
        r"^microsoft/",
        include("microsoft_auth.urls", namespace="microsoft_auth"),
    ),
]
