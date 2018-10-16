from django.urls import path
from .views import *
from django.contrib.auth.decorators import login_required
app_name = 'settings'
urlpatterns = [
    path('', SettingsView.as_view(), name='settings'),
    path('myaccount/', login_required(MyAccountView.as_view()), name='MyAccount'),
    path('accountmanagement/', AccountManagementView.as_view(), name='AccountManagement')
]