from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.urls import path
from . import views
from . import apis

LOGIN_URL = getattr(settings, 'LOGIN_URL')
app_name = 'projects'
urlpatterns = [
    path('', login_required(views.ProjectsView.as_view(), redirect_field_name=LOGIN_URL), name='projects'),
    path('<int:id>/', login_required(views.ProjectsDetailView.as_view(), redirect_field_name=LOGIN_URL), name='projectdetail'),
    path('<int:id>/detailed', login_required(views.ProjectsDetailView.as_view(), redirect_field_name=LOGIN_URL), name='projectdetail'),
    path('<int:id>/scantasks', login_required(views.ProjectsScanTaskView.as_view(), redirect_field_name=LOGIN_URL), name='projectsscantaskview'),

    # APIs
    path('api/getprojectvulns', apis.APIGetProjectVulns.as_view(), name='getprojectvulns'),
    path('api/getprojectname', apis.APIGetProjectName.as_view(), name='getprojectname'),
    path('api/getprojects', apis.APIGetProjects.as_view(), name='getprojects'),
    path('api/getprojectbyid', apis.APIGetProjectByID.as_view(), name='APIgethostbyid'),
    path('api/addproject', apis.APIAddProject.as_view(), name='APIaddproject'),
    path('api/deleteproject', apis.APIDeleteProject.as_view(), name='APIdeleteproject'),
    path('api/updateproject', apis.APIUpdateProject.as_view(), name='APIupdateproject'),
]