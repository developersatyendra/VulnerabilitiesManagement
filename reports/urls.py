from django.urls import path
from . import views

app_name = 'reports'
urlpatterns = [
    path('', views.ReportsView.as_view(), name='reports'),
    path('<int:id>', views.ReportDetailView.as_view(), name='reportDetail'),
    path('testhtml/', views.ReportTestHTML.as_view(), name='reportDetail'),
]