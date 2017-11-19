from django.conf.urls import include, url

urlpatterns = [
    url(r'^microsoft/', include('microsoft_auth.urls', namespace='microsoft')),
]
