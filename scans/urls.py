from django.urls import path
from . import views
from . import apis

app_name='scans'
urlpatterns = [
    path('', views.ScansView.as_view(), name='scans'),
    path('<int:id>', views.ScansDetailView.as_view(), name='scanDetail'),

    # APIs
    path('api/getscans', apis.APIGetScans.as_view(), name='APIgetscans'),
    path('api/getscanbyid', apis.APIGetScanByID.as_view(), name='APIgetscanbyid'),
    path('api/addscan', apis.APIAddScan.as_view(), name='APIaddscan'),
    path('api/deletescan', apis.APIDeleteScan.as_view(), name='APIdeletescan'),
    path('api/updatescan', apis.APIUpdateScan.as_view(), name='APIupdatescan'),
    path('api/getattachment', apis.APIGetScanAttachment.as_view(), name='APIgetattachment'),
    path('api/addattachment', apis.APIAddAttachment.as_view(), name='APIaddattachment'),
    path('api/deleteattachment', apis.APIDeleteAttachment.as_view(), name='APIdeleteattachment'),
]