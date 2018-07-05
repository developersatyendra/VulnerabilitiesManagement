from django.urls import path
from . import views

app_name = 'vulnerabilities'
urlpatterns = [
    path('', views.VulnerabilitiesView.as_view(), name='vulnerabilities'),
    path('<int:id>', views.VulnerabilityDetailView.as_view(), name='vulnerabilityDetail'),
    path('getvulns', views.APIGetVulns.as_view(), name='APIgetvulns'),
    path('api/addvulns', views.APIAddVuln.as_view(), name='APIaddvulns'),
    path('api/deleteservice', views.APIDeleteVuln.as_view(),name='APIdelvulns'),

]