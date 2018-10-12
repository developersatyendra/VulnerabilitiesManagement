from django.contrib.auth.views import logout
from django.urls import path
from .views import AccountLogin
from .apis import *
app_name = 'accounts'
urlpatterns = [
    path('login', AccountLogin, name='login'),
    path('logout', logout, name='logout'),

    # APIs
    path('api/getmyaccount', APIGetMyAccount.as_view(), name='GetMyAccount'),
    path('api/changemypassword', APIChangeMyPassword.as_view(), name='ChangeMyPassword'),
    path('api/updatemyaccount', APIUpdateMyAccount.as_view(), name='UpdateMyAccount')
]