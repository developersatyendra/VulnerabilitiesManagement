from django.urls import path
from . import views

app_name='services'
urlpatterns = [
    path('', views.ServicesView.as_view(), name='services'),
    path('<int:id>/', views.ServiceDetailView.as_view(), name='serviceDetail'),
    path('api/getservices', views.APIGetServices.as_view(), name='APIgetservices'),
    path('api/getservicebyid', views.APIGetServicesByID.as_view(), name='APIgetservicebyid'),
    path('api/addservice', views.APIAddService.as_view(), name='APIaddservice'),
    path('api/deleteservice', views.APIDeleteService.as_view(), name='APIdeleteservice'),
    path('api/updateservice', views.APIUpdateService.as_view(), name='APIupdateservice'),
]