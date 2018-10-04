from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views
from django.conf import settings

LOGIN_URL = getattr(settings, 'LOGIN_URL')
app_name='dashboard'
urlpatterns = [
    path('', login_required(views.DashboardView.as_view(),redirect_field_name=LOGIN_URL), name='dashboard'),
]