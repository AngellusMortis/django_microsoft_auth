from django.contrib import admin
from django.conf.urls import include, url

urlpatterns = [
    url(r"^admin/", admin.site.urls),
    url(
        r"^microsoft/",
        include("microsoft_auth.urls", namespace="microsoft_auth"),
    ),
]
