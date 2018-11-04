from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.urls import path
from . import views, apis

LOGIN_URL = getattr(settings, 'LOGIN_URL')
app_name = 'vulnerabilities'
urlpatterns = [
    path('', login_required(views.VulnerabilitiesView.as_view(), redirect_field_name=LOGIN_URL), name='vulnerabilities'),
    path('<int:id>/', login_required(views.VulnerabilityDetailView.as_view(), redirect_field_name=LOGIN_URL), name='vulnerabilityDetail'),
    path('<int:id>/detailed', login_required(views.VulnerabilityDetailView.as_view(), redirect_field_name=LOGIN_URL), name='vulnerabilityDetail'),
    path('<int:id>/hostinvolved', login_required(views.HostInvolvedView.as_view(), redirect_field_name=LOGIN_URL), name='hostInvoled'),
    
    # APIs
    path('api/getcurrenthostvuln', apis.APIGetCurrentHostVuln.as_view(), name='APIgetcurrenthostvuln'),
    path('api/getcurrentprojectvuln', apis.APIGetCurrentProjectVuln.as_view(), name='APIgetcurrentprojectvuln'),
    path('api/getcurrentglobalvuln', apis.APIGetCurrentGlobalVuln.as_view(), name='APIgetcurrentglobalvuln'),
    path('api/getvulnname', apis.APIGetVulnName.as_view(), name='APIgetvulnname'),
    path('api/getvulns', apis.APIGetVulns.as_view(), name='APIgetvulns'),
    path('api/getvulnbyid', apis.APIGetVulnByID.as_view(), name='APIgetvulnbyid'),
    path('api/addvuln', apis.APIAddVuln.as_view(), name='APIaddvulns'),
    path('api/deletevuln', apis.APIDeleteVuln.as_view(),name='APIdelvulns'),
    path('api/updatevuln', apis.APIUpdateVuln.as_view(),name='APIupdatevulns'),
]