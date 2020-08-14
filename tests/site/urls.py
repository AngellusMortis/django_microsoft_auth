from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("accounts/", include("django.contrib.auth.urls")),
    path("admin/", admin.site.urls),
    path(
        "microsoft/",
        include("microsoft_auth.urls", namespace="microsoft_auth"),
    ),
]
