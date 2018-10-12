from django.utils.datastructures import MultiValueDictKeyError
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.models import User
from .forms import CustomChangePasswordForm, AccountUpdateMyInfoForm
from django.contrib.auth import update_session_auth_hash
from .serializers import UserSerializer

PAGE_DEFAULT = 1
NUM_ENTRY_DEFAULT = 50


######################################################
#   APIGetProjectName get Name of Project from id
#

class APIChangeMyPassword(APIView):
    def post(self, request):
        form = CustomChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            return Response({'status': '0', 'message': 'Your password was successfully updated!'})
        else:
            return Response({'status': '-1', 'message': 'Change password is failed', 'detail': form.errors})


######################################################
#   APIGetProjectName get Name of Project from id
#

class APIGetMyAccount(APIView):
    def get(self, request):
        object = UserSerializer(User.objects.get(username=request.user))
        return Response({'status': '0', 'object': object.data})


class APIUpdateMyAccount(APIView):
    def post(self, request):
        user = User.objects.get(username=request.user)
        form = AccountUpdateMyInfoForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return Response({'status':0, 'message': 'Your account inforation is updated'})
        else:
            return Response({'status': '-1', 'message': 'Form is invalid', 'detail': form.errors})

