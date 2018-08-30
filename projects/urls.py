from django.urls import path
from . import views
from . import apis

app_name = 'projects'
urlpatterns = [
    path('', views.ProjectsView.as_view(), name='projects'),
    path('<int:id>/', views.ProjectsDetailView.as_view(), name='projectdetail'),
    path('<int:id>/detailed', views.ProjectsDetailView.as_view(), name='projectdetail'),
    path('<int:id>/scantasks', views.ProjectsScanTaskView.as_view(), name='projectsscantaskview'),

    # APIs
    path('api/getprojectname', apis.APIGetProjectName.as_view(), name='getprojectname'),
    path('api/getprojects', apis.APIGetProjects.as_view(), name='getprojects'),
    path('api/getprojectbyid', apis.APIGetProjectByID.as_view(), name='APIgethostbyid'),
    path('api/addproject', apis.APIAddProject.as_view(), name='APIaddproject'),
    path('api/deleteproject', apis.APIDeleteProject.as_view(), name='APIdeleteproject'),
    path('api/updateproject', apis.APIUpdateProject.as_view(), name='APIupdateproject'),
]