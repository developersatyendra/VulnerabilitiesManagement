from django.urls import path
from . import views

app_name = 'vulnerabilities'
urlpatterns = [
    path('', views.VulnerabilitiesView.as_view(), name='vulnerabilities'),
    path('<int:id>', views.VulnerabilityDetailView.as_view(), name='vulnerabilityDetail'),
    path('api/getvulns', views.APIGetVulns.as_view(), name='APIgetvulns'),
    path('api/getvulnbyid', views.APIGetVulnByID.as_view(), name='APIgetvulnbyid'),
    path('api/addvulns', views.APIAddVuln.as_view(), name='APIaddvulns'),
    path('api/deletevuln', views.APIDeleteVuln.as_view(),name='APIdelvulns'),
    path('api/updatevuln', views.APIUpdateVuln.as_view(),name='APIupdatevulns'),
]