from django.urls import path
from . import views

app_name = 'hosts'
urlpatterns = [
    path('', views.HostsView.as_view(), name='hosts'),
    path('<int:id>', views.HostDetailView.as_view(), name='hostDetail'),
    path('api/gethosts', views.APIGetHosts.as_view(), name='APIgethost'),
    path('api/gethostbyid', views.APIGetHostsByID.as_view(), name='APIgethostbyid'),
    path('api/addhost', views.APIAddHost.as_view(), name='APIaddhost'),
    path('api/deletehost', views.APIDeleteHost.as_view(), name='APIdeletehost'),
    path('api/updatehost', views.APIUpdateHost.as_view(), name='APIupdatehost'),
]