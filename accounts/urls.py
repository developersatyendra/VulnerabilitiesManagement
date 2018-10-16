from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from .views import AccountLogin
from .apis import *
app_name = 'accounts'
urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),

    # APIs
    # My Account
    path('api/getmyaccount', APIGetMyAccount.as_view(), name='GetMyAccount'),
    path('api/changemypassword', APIChangeMyPassword.as_view(), name='ChangeMyPassword'),
    path('api/updatemyaccount', APIUpdateMyAccount.as_view(), name='UpdateMyAccount'),

    # Account Management
    path('api/createaccount', APICreateAccount.as_view(), name='CreateAccount'),
    path('api/getaccounts', APIGetAccounts.as_view(), name='GetAccounts'),
    path('api/editaccount', APIEditAccount.as_view(), name='EditAccounts'),
    path('api/resetpasswordaccount', APIResetPasswordAccount.as_view(), name='ResetPasswordAccounts'),
]