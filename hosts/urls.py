from django.urls import path
from . import views
from . import apis

app_name = 'hosts'
urlpatterns = [
    path('', views.HostsView.as_view(), name='hosts'),
    path('<int:id>', views.HostDetailView.as_view(), name='hostDetail'),

    # APIs
    path('api/gethosts', apis.APIGetHosts.as_view(), name='APIgethost'),
    path('api/gethostbyid', apis.APIGetHostsByID.as_view(), name='APIgethostbyid'),
    path('api/addhost', apis.APIAddHost.as_view(), name='APIaddhost'),
    path('api/deletehost', apis.APIDeleteHost.as_view(), name='APIdeletehost'),
    path('api/updatehost', apis.APIUpdateHost.as_view(), name='APIupdatehost'),
]