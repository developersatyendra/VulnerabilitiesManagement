from django.urls import path
from . import views, apis

app_name = 'vulnerabilities'
urlpatterns = [
    path('', views.VulnerabilitiesView.as_view(), name='vulnerabilities'),
    path('<int:id>', views.VulnerabilityDetailView.as_view(), name='vulnerabilityDetail'),
    
    # APIs
    path('api/getvulns', apis.APIGetVulns.as_view(), name='APIgetvulns'),
    path('api/getvulnbyid', apis.APIGetVulnByID.as_view(), name='APIgetvulnbyid'),
    path('api/addvuln', apis.APIAddVuln.as_view(), name='APIaddvulns'),
    path('api/deletevuln', apis.APIDeleteVuln.as_view(),name='APIdelvulns'),
    path('api/updatevuln', apis.APIUpdateVuln.as_view(),name='APIupdatevulns'),
]