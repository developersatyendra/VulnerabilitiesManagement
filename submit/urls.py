from django.urls import path
from . import views
from . import apis

app_name = 'submit'
urlpatterns = [
    path('', views.SubmitsView.as_view(), name='submit'),

    # APIs
    path('api/getsubmits', apis.APIGetSubmits.as_view(), name='APIgetsubmits'),
    path('api/addsubmit', apis.APIAddSubmit.as_view(), name='APIaddsubmit'),
    path('api/deletesubmit', apis.APIDeleteSubmit.as_view(), name='APIdeletesubmit'),
]