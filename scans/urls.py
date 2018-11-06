from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.urls import path
from . import views
from . import apis

LOGIN_URL = getattr(settings, 'LOGIN_URL')
app_name='scans'
urlpatterns = [
    path('', login_required(views.ScansView.as_view(), redirect_field_name=LOGIN_URL), name='scans'),
    path('<int:id>/', login_required(views.ScanStatisticsView.as_view(), redirect_field_name=LOGIN_URL), name='scanDetail'),
    path('<int:id>/detailed', login_required(views.ScansDetailView.as_view(), redirect_field_name=LOGIN_URL), name='scanDetail'),
    path('<int:id>/hostscanned', login_required(views.ScanHostsView.as_view(), redirect_field_name=LOGIN_URL), name='scanHostsview'),
    path('<int:id>/statistics', login_required(views.ScanStatisticsView.as_view(), redirect_field_name=LOGIN_URL), name='scanStatisticsview'),

    # APIs
    path('api/getscanname', apis.APIGetScanName.as_view(), name='APIgetscanname'),
    path('api/getscansvulns', apis.APIGetScansVuln.as_view(), name='APIgetscansvulns'),

    path('api/getscans', apis.APIGetScans.as_view(), name='APIgetscans'),
    path('api/getscanbyid', apis.APIGetScanByID.as_view(), name='APIgetscanbyid'),
    path('api/addscan', apis.APIAddScan.as_view(), name='APIaddscan'),
    path('api/deletescan', apis.APIDeleteScan.as_view(), name='APIdeletescan'),
    path('api/updatescan', apis.APIUpdateScan.as_view(), name='APIupdatescan'),
    path('api/getattachment', apis.APIGetScanAttachment.as_view(), name='APIgetattachment'),
    path('api/addattachment', apis.APIAddAttachment.as_view(), name='APIaddattachment'),
    path('api/deleteattachment', apis.APIDeleteAttachment.as_view(), name='APIdeleteattachment'),
]