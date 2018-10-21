from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.urls import path
from . import views
from . import apis

LOGIN_URL = getattr(settings, 'LOGIN_URL')
app_name='services'
urlpatterns = [
    path('', login_required(views.ServicesView.as_view(), redirect_field_name=LOGIN_URL), name='services'),
    path('<int:id>/', login_required(views.ServiceDetailView.as_view(), redirect_field_name=LOGIN_URL), name='serviceDetail'),
    path('<int:id>/detailed', login_required(views.ServiceDetailView.as_view(), redirect_field_name=LOGIN_URL), name='serviceDetail'),
    path('<int:id>/relevantvuln', login_required(views.ServiceRelevantVulnView.as_view(), redirect_field_name=LOGIN_URL), name='serviceRelevantVulnDetail'),
    path('<int:id>/runningonhost', login_required(views.ServiceRunOnHostView.as_view(), redirect_field_name=LOGIN_URL), name='serviceRunningOnHost'),

    # APIs
    path('api/getservices', apis.APIGetServices.as_view(), name='APIGetServices'),
    path('api/getservicebyid', apis.APIGetServicesByID.as_view(), name='APIGetServiceByID'),
    path('api/getservicevulnstat', apis.APIServiceVulnStatistic.as_view(), name='APIGetServiceVulnStat'),
    path('api/addservice', apis.APIAddService.as_view(), name='APIAddService'),
    path('api/deleteservice', apis.APIDeleteService.as_view(), name='APIDeleteService'),
    path('api/updateservice', apis.APIUpdateService.as_view(), name='APIUpdateService'),
]