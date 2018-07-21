from django.urls import path
from . import views

app_name = 'projects'
urlpatterns = [
    path('', views.ProjectsView.as_view(), name='projects'),
    # path('<int:id>', views.ProjectDetailView.as_view(), name='projectDetail'),
    path('api/getprojects', views.APIGetProjects.as_view(), name='getprojects'),
    path('api/getprojectbyid', views.APIGetProjectByID.as_view(), name='APIgethostbyid'),
    path('api/addproject', views.APIAddProject.as_view(), name='APIaddproject'),
    path('api/deleteproject', views.APIDeleteProject.as_view(), name='APIdeleteproject'),
    path('api/updateproject', views.APIUpdateProject.as_view(), name='APIupdateproject'),
]