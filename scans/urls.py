from django.urls import path
from . import views

app_name='scans'
urlpatterns = [
    path('', views.ScansView.as_view(), name='scans'),
    # path('<int:id>', views.ScanDetailView.as_view(), name='scanDetail'),
]