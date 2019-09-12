from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


@login_required
def home(request):
    return HttpResponse("<html><body><h1>Welcome to Home!</h1></body></html>")
