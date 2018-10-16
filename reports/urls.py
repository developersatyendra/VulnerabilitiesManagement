from django.contrib.auth.decorators import login_required, permission_required
from django.conf import settings
from django.urls import path
from . import views
from . import apis


LOGIN_URL = getattr(settings, 'LOGIN_URL')
app_name = 'reports'
urlpatterns = [
    path('',  login_required(views.ReportProjectView.as_view(), redirect_field_name=LOGIN_URL), name='reports'),
    path('hostreports', login_required(login_required(views.ReportHostView.as_view()),redirect_field_name=LOGIN_URL), name='hostReport'),
    path('scanreports', login_required(views.ReportScanView.as_view(), redirect_field_name=LOGIN_URL), name='scanReport'),
    path('projectreports', login_required(views.ReportProjectView.as_view(), redirect_field_name=LOGIN_URL), name='projectReport'),

    # APIs
    path('api/getreportfile', apis.APIGetReportFile.as_view(), name='getReportFile'),
    path('api/getreportbyid', apis.APIGetReportByID.as_view(), name='getReportByID'),
    path('api/getreports', apis.APIGetReports.as_view(), name='getReports'),
    path('api/addreport', apis.APIAddReport.as_view(), name='addReport'),
    path('api/deletereport', apis.APIDeleteReport.as_view(), name='deleteReports'),
]