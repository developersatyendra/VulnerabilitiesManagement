from django.urls import path
from . import views
from . import apis

app_name='services'
urlpatterns = [
    path('', views.ServicesView.as_view(), name='services'),
    path('<int:id>/', views.ServiceDetailView.as_view(), name='serviceDetail'),

    # APIs
    path('api/getservices', apis.APIGetServices.as_view(), name='APIgetservices'),
    path('api/getservicebyid', apis.APIGetServicesByID.as_view(), name='APIgetservicebyid'),
    path('api/addservice', apis.APIAddService.as_view(), name='APIaddservice'),
    path('api/deleteservice', apis.APIDeleteService.as_view(), name='APIdeleteservice'),
    path('api/updateservice', apis.APIUpdateService.as_view(), name='APIupdateservice'),
]