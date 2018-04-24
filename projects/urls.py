from django.urls import path
from . import views

app_name = 'projects'
urlpatterns = [
    path('', views.ProjectsView.as_view(), name='projects'),
    path('<int:id>', views.ProjectDetailView.as_view(), name='projectDetail'),
]