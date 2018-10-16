from django.utils.datastructures import MultiValueDictKeyError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.models import User
from .forms import *
from django.contrib.auth import update_session_auth_hash
from .serializers import UserSerializer, AccountSerializer

PAGE_DEFAULT = 1
NUM_ENTRY_DEFAULT = 50


######################################################
#   APIChangeMyPassword
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
#   APIGetMyAccount
#

class APIGetMyAccount(APIView):
    def get(self, request):
        object = UserSerializer(User.objects.get(username=request.user))
        return Response({'status': '0', 'object': object.data})


######################################################
#   APIUpdateMyAccount
#
class APIUpdateMyAccount(APIView):
    def post(self, request):
        user = User.objects.get(username=request.user)
        form = AccountUpdateMyInfoForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return Response({'status':0, 'message': 'Your account inforation is updated'})
        else:
            return Response({'status': '-1', 'message': 'Form is invalid', 'detail': form.errors})


######################################################
#   APIUpdateMyAccount
#
class APICreateAccount(APIView):
    permission_classes = (IsAdminUser,)

    def post(self, request):

        form = AccountCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return Response({'status':0, 'message': '{} account is created'.format(user.username)})
        else:
            return Response({'status': '-1', 'message': 'Form is invalid', 'detail': form.errors})


class APIGetAccounts(APIView):
    permission_classes = (IsAdminUser,)

    def get(self, request):
        users = User.objects.all()

        # Filter by search keyword
        if request.GET.get('searchText'):
            search = request.GET.get('searchText')
            query = Q(username__icontains=search) \
                    | Q(first_name__icontains=search) \
                    | Q(last_name__icontains=search) \
                    | Q(email__icontains=search)
            users = users.filter(query)

        # get total
        numObject = users.count()
        # Get sort order
        if request.GET.get('sortOrder') == 'asc':
            sortString = ''
        else:
            sortString = '-'

        # Get sort filed
        if request.GET.get('sortName'):
            sortString = sortString + request.GET.get('sortName')
        else:
            sortString = sortString + 'id'
        querySet = users.order_by(sortString)

        # Get Page Number
        if request.GET.get('pageNumber'):
            page = request.GET.get('pageNumber')
        else:
            page = PAGE_DEFAULT

        # Get Page Size
        if request.GET.get('pageSize'):
            numEntry = request.GET.get('pageSize')
            # IF Page size is 'ALL'
            if numEntry.lower() == 'all' or numEntry == -1:
                numEntry = numObject
        else:
            numEntry = NUM_ENTRY_DEFAULT
        querySetPaged = Paginator(querySet, int(numEntry))
        dataPaged = querySetPaged.get_page(page)
        dataSerialized = AccountSerializer(dataPaged, many=True)
        data = dict()
        data["total"] = numObject
        data['rows'] = dataSerialized.data
        return Response({'status': 0, 'object': data})


class APIEditAccount(APIView):

    permission_classes = (IsAdminUser,)

    def post(self, request):
        try:
            user = User.objects.get(pk=request.POST.get('id'))
        except (User.DoesNotExist, ValueError, TypeError) as e:
            return Response({'status': '-1', 'message': 'Some thing go wrong'})
        form = AccountEditForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            return Response({'status': 0, 'message': '{} account is updated'.format(user.username)})
        else:
            return Response({'status': '-1', 'message': 'Form is invalid', 'detail': form.errors})


class APIResetPasswordAccount(APIView):
    permission_classes = (IsAdminUser,)

    def post(self, request):
        try:
            user = User.objects.get(pk=request.POST.get('id'))
        except (User.DoesNotExist, ValueError, TypeError) as e:
            return Response({'status': '-1', 'message': 'Some thing go wrong'})
        form = AccountResetPasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password2']
            user.set_password(password)
            user.save()
            update_session_auth_hash(request, user)  # Important!
            return Response({'status': 0, 'message': '{} password account is updated'.format(user.username)})
        else:
            return Response({'status': '-1', 'message': 'Form is invalid', 'detail': form.errors})