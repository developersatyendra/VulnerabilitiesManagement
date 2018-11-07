from django.urls import path
from .views import *
from django.contrib.auth.decorators import login_required
from django.views.generic.base import RedirectView


app_name = 'settings'
urlpatterns = [
    path('', RedirectView.as_view(url='/settings/myaccount'), name='settings'),
    path('myaccount/', login_required(MyAccountView.as_view()), name='MyAccount'),
    path('accountmanagement/', AccountManagementView.as_view(), name='AccountManagement'),
    path('about/', AboutView.as_view(), name='About')
]