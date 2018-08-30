from django.utils.datastructures import MultiValueDictKeyError
from .models import HostModel
from .forms import HostForm, HostIDForm
from .serializers import HostSerializer
from django.contrib.auth.models import User
from rest_framework.views import APIView
from django.core.paginator import Paginator
from django.db.models import Q
from rest_framework.response import Response

PAGE_DEFAULT = 1
NUM_ENTRY_DEFAULT = 50


#
# APIGetHosts get host from these params:
#   searchText: Search content
#   sortName: Name of column is applied sort
#   sortOrder: sort entry by order 'asc' or 'desc'
#   pageSize: number of entry per page
#   pageNumber: page number of current view
#   advFilter: "projectID", "hostID", "vulnID"
#   advFilterValue: Value to be used to filter

# class APIGetHosts(APIView):
#     def get(self, request):
#         numObject = HostModel.objects.all().count()
#
#         # Filter by search keyword
#         if request.GET.get('searchText'):
#             search = request.GET.get('searchText')
#             query = Q(ipAddr__icontains=search)\
#                     | Q(hostName__icontains=search)\
#                     | Q(osName__icontains=search) \
#                     | Q(osVersion__icontains=search) \
#                     | Q(description__icontains=search)
#             querySet = HostModel.objects.filter(query)
#         else:
#             querySet = HostModel.objects.all()
#
#         # Get sort order
#         if request.GET.get('sortOrder') == 'asc':
#             sortString = ''
#         else:
#             sortString = '-'
#
#         # Get sort filed
#         if request.GET.get('sortName'):
#             sortString = sortString + request.GET.get('sortName')
#         else:
#             sortString = sortString + 'id'
#         querySet = querySet.order_by(sortString)
#
#         # Get Page Number
#         if request.GET.get('pageNumber'):
#             page = request.GET.get('pageNumber')
#         else:
#             page = PAGE_DEFAULT
#
#         # Get Page Size
#         if request.GET.get('pageSize'):
#             numEntry = request.GET.get('pageSize')
#             # IF Page size is 'ALL'
#             if numEntry.lower() == 'all' or numEntry == -1:
#                 numEntry = numObject
#         else:
#             numEntry = NUM_ENTRY_DEFAULT
#         querySetPaged = Paginator(querySet, int(numEntry))
#         dataPaged = querySetPaged.get_page(page)
#         dataSerialized = HostSerializer(dataPaged, many=True)
#         data = dict()
#         data["total"] = numObject
#         data['rows'] = dataSerialized.data
#         return Response({'status': 0, 'object':data})


class APIGetHosts(APIView):
    def get(self, request):
        numObject = HostModel.objects.all().count()

        # Filter by search keyword
        if request.GET.get('searchText'):
            search = request.GET.get('searchText')
            query = Q(ipAddr__icontains=search)\
                    | Q(hostName__icontains=search)\
                    | Q(osName__icontains=search) \
                    | Q(osVersion__icontains=search) \
                    | Q(description__icontains=search)
            querySet = HostModel.objects.filter(query)
        else:
            querySet = HostModel.objects.all()

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
        querySet = querySet.order_by(sortString)

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
        dataSerialized = HostSerializer(dataPaged, many=True)
        data = dict()
        data["total"] = numObject
        data['rows'] = dataSerialized.data
        return Response({'status': 0, 'object':data})


#
# APIGetHostsByID get hosts from ids
# return {'retVal': '-1'} if id not found
# return Host object if it's success
#

class APIGetHostsByID(APIView):
    def get(self, request):
        if request.GET.get('id'):
            id = request.GET.get('id')
            try:
                retHost = HostModel.objects.get(pk=id)
            except (HostModel.DoesNotExist, ValueError):
                return Response({'status': '-1', 'message': 'Value error',
                                 'detail': {"id": [{"message": "ID is not integer", "code": "value error"}]}})
            dataSerialized = HostSerializer(retHost, many=False)
            return Response(dataSerialized.data)
        else:
            return Response({'status': '-1', 'message': 'fields are required',
                             'detail': {"id": [{"message": "ID is required", "code": "required"}]}})


#
# APIAddHost add new Host
# return {'retVal': '-1'} if id not found
# return Host object if it's success
#

class APIAddHost(APIView):
    def post(self, request):
        hostForm = HostForm(request.POST)
        if hostForm.is_valid():
            entry = hostForm.save(commit=False)
            entry.createBy = User.objects.get(pk=1)
            entry.save()
            dataSerialized = HostSerializer(entry, many=False)
            return Response({'status': '0', 'object': dataSerialized.data})
        else:
            return Response({'status': '-1', 'message': 'Form is invalid', 'detail': hostForm.errors})



#
# APIDeleteHost delete existing Host
# return {'retVal': '-1'} if id not found
# return number of Host object deleted if it's success
#

class APIDeleteHost(APIView):
    def post(self, request):
        hostForm = HostIDForm(request.POST)
        if hostForm.is_valid():
            successOnDelete = 0
            try:
                ids = hostForm.data['id'].split(',')
            except MultiValueDictKeyError:
                return Response({'status': '-1', 'message': 'Fields are required',
                                 'detail': {"id": [{"message": "ID is required", "code": "required"}]}})
            for rawID in ids:
                try:
                    id = int(rawID)
                except ValueError:
                    pass
                else:
                    try:
                        retService = HostModel.objects.get(pk=id)
                    except HostModel.DoesNotExist:
                        pass
                    else:
                        retService.delete()
                        successOnDelete = successOnDelete + 1
            if successOnDelete==1:
                return Response(
                    {'status': '0', 'message': '1 host is successfully deleted.', 'numDeleted': successOnDelete})
            else:
                return Response(
                            {'status': '0', 'message': '{} hosts are successfully deleted.'.format(successOnDelete), 'numDeleted': successOnDelete})
        else:
            return Response({'status': '-1', 'message': 'Form is invalid', 'detail': {hostForm.errors}})


#
# APIUpdateService delete existing host
# return {'notification': 'error_msg'} if id not found
# return host object if it's success
#

class APIUpdateHost(APIView):
    def post(self, request):
        if request.POST.get('id'):
            try:
                id = request.POST.get('id')
            except ValueError:
                return Response({'status': '-1', 'message': 'Value error',
                                 'detail': {"id": [{"message": "ID is not integer", "code": "value error"}]}})
            hostObj = HostModel.objects.get(pk=id)
            hostForm = HostForm(request.POST, instance=hostObj)
        else:
            return Response({'status': '-1', 'message': 'Fields are required',
                             'detail': {"id": [{"message": "ID is required", "code": "required"}]}})
        if hostForm.is_valid():
            entry = hostForm.save()
            dataSerialized = HostSerializer(entry, many=False)
            return Response({'status': '0', 'object': dataSerialized.data})
        else:
            return Response({'status': '-1', 'message': 'Form is invalid', 'detail': hostForm.errors})