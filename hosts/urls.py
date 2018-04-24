from django.urls import path
from . import views

app_name = 'hosts'
urlpatterns = [
    path('', views.HostsView.as_view(), name='hosts'),
    path('<int:id>', views.HostDetailView.as_view(), name='hostDetail'),
]