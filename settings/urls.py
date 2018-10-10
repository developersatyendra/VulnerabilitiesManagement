from django.urls import path
from .views import *

app_name = 'settings'
urlpatterns = [
    path('', SettingsView.as_view(), name='settings'),
    path('myaccount/', MyAccountView.as_view(), name='MyAccount')
]