from django.shortcuts import render
from django.contrib.auth.views import login, logout
from django.conf import settings
from django.http import HttpResponseRedirect

HOME_DIR = getattr(settings, "LOGIN_REDIRECT_URL")

def AccountLogin(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(HOME_DIR)
    else:
        return login(request)

