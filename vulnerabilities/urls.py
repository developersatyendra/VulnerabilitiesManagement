from django.urls import path
from . import views

app_name = 'vulnerabilities'
urlpatterns = [
    path('', views.VulnerabilitiesView.as_view(), name='vulnerabilities'),
    path('<int:id>', views.VulnerabilityDetailView.as_view(), name='vulnerabilityDetail'),
]