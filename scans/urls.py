from django.urls import path
from . import views

app_name='scans'
urlpatterns = [
    path('', views.ScansView.as_view(), name='scans'),
    # path('<int:id>', views.ScanDetailView.as_view(), name='scanDetail'),
    path('api/getscans', views.APIGetScans.as_view(), name='APIgetscans'),
    path('api/getscanbyid', views.APIGetScanByID.as_view(), name='APIgetscanbyid'),
    path('api/addscan', views.APIAddScan.as_view(), name='APIaddscan'),
    path('api/deletescan', views.APIDeleteScan.as_view(), name='APIdeletescan'),
    path('api/updatescan', views.APIUpdateScan.as_view(), name='APIupdatescan'),
]