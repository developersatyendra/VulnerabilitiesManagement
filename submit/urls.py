from django.urls import path
from . import views

app_name = 'submit'
urlpatterns = [
    path('', views.SubmitsView.as_view(), name='submit'),
    path('api/getsubmits', views.APIGetSubmits.as_view(), name='APIgetsubmits'),
    path('api/addsubmit', views.APIAddSubmit.as_view(), name='APIaddsubmit'),
]