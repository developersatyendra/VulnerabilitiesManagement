from django.urls import path
from . import views
from . import apis

app_name = 'hosts'
urlpatterns = [
    path('', views.HostsView.as_view(), name='hosts'),
    path('<int:id>/', views.HostDetailView.as_view(), name='hostDetail'),
    path('<int:id>/detailed', views.HostDetailView.as_view(), name='hostDetail'),
    path('<int:id>/scantask', views.HostScanTaskView.as_view(), name='hostDetail'),
    path('<int:id>/currentvuln', views.HostCurrentVulnView.as_view(), name='hostDetail'),
    path('<int:id>/runningservice', views.HostRunningServiceView.as_view(), name='hostrunningservice'),

    # APIs
    path('api/gethostname', apis.APIGetHostName.as_view(), name='APIgethostname'),
    path('api/gethostsvuln', apis.APIGetHostsVuln.as_view(), name='APIgethostsvuln'),
    path('api/gethosts', apis.APIGetHosts.as_view(), name='APIgethosts'),
    path('api/gethostbyid', apis.APIGetHostsByID.as_view(), name='APIgethostbyid'),
    path('api/addhost', apis.APIAddHost.as_view(), name='APIaddhost'),
    path('api/deletehost', apis.APIDeleteHost.as_view(), name='APIdeletehost'),
    path('api/updatehost', apis.APIUpdateHost.as_view(), name='APIupdatehost'),
]