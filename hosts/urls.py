from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.urls import path
from . import views
from . import apis

LOGIN_URL = getattr(settings, 'LOGIN_URL')
app_name = 'hosts'
urlpatterns = [
    path('', login_required(views.HostsView.as_view(), redirect_field_name=LOGIN_URL), name='hosts'),
    path('<int:id>/', login_required(views.HostDetailView.as_view(), redirect_field_name=LOGIN_URL), name='hostDetail'),
    path('<int:id>/detailed', login_required(views.HostDetailView.as_view(), redirect_field_name=LOGIN_URL), name='hostDetail'),
    path('<int:id>/scantask', login_required(views.HostScanTaskView.as_view(), redirect_field_name=LOGIN_URL), name='hostDetail'),
    path('<int:id>/currentvuln', login_required(views.HostCurrentVulnView.as_view(), redirect_field_name=LOGIN_URL), name='hostDetail'),
    path('<int:id>/runningservice', login_required(views.HostRunningServiceView.as_view(), redirect_field_name=LOGIN_URL), name='hostrunningservice'),

    # APIs
    path('api/gethostname', apis.APIGetHostName.as_view(), name='APIgethostname'),
    path('api/gethostsvuln', apis.APIGetHostsVuln.as_view(), name='APIgethostsvuln'),
    path('api/gethosts', apis.APIGetHosts.as_view(), name='APIgethosts'),
    path('api/gethostsos', apis.APIGetHostsOS.as_view(), name='APIgethostsOS'),
    path('api/gethostbyid', apis.APIGetHostsByID.as_view(), name='APIgethostbyid'),
    path('api/addhost', apis.APIAddHost.as_view(), name='APIaddhost'),
    path('api/deletehost', apis.APIDeleteHost.as_view(), name='APIdeletehost'),
    path('api/updatehost', apis.APIUpdateHost.as_view(), name='APIupdatehost'),
]