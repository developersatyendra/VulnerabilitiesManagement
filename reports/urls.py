from django.urls import path
from . import views
from . import apis
app_name = 'reports'
urlpatterns = [
    path('', views.ReportProjectView.as_view(), name='reports'),
    path('hostreports', views.ReportHostView.as_view(), name='hostReport'),
    path('scanreports', views.ReportScanView.as_view(), name='scanReport'),
    path('projectreports', views.ReportProjectView.as_view(), name='projectReport'),

    # APIs
    path('api/getreportfile', apis.APIGetReportFile.as_view(), name='getReportFile'),
    path('api/getreportbyid', apis.APIGetReportByID.as_view(), name='getReportByID'),
    path('api/getreports', apis.APIGetReports.as_view(), name='getReports'),
    path('api/addreport', apis.APIAddReport.as_view(), name='addReport'),
    path('api/deletereport', apis.APIDeleteReport.as_view(), name='deleteReports'),
]