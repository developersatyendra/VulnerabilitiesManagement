from django.contrib.auth.views import logout
from django.urls import path
from .views import AccountLogin
app_name = 'accounts'
urlpatterns = [
    path('login', AccountLogin, name='login'),
    path('logout', logout, name='logout'),
]