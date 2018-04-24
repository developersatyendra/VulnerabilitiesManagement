from django.urls import path
from . import views

app_name = 'submit'
urlpatterns = [
    path('', views.SubmitView.as_view(), name='submit'),
]