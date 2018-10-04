from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.urls import path
from . import views
from . import apis

LOGIN_URL = getattr(settings, 'LOGIN_URL')
app_name = 'submit'
urlpatterns = [
    path('', login_required(views.SubmitsView.as_view(), redirect_field_name=LOGIN_URL), name='submit'),

    # APIs
    path('api/getsubmits', apis.APIGetSubmits.as_view(), name='APIgetsubmits'),
    path('api/addsubmit', apis.APIAddSubmit.as_view(), name='APIaddsubmit'),
    path('api/deletesubmit', apis.APIDeleteSubmit.as_view(), name='APIdeletesubmit'),
    path('api/getsubmitfile', apis.APIGetSubmitFile.as_view(), name='APIgetsubmitfile'),
]