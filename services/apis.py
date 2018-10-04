from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.models import User
from hosts.models import HostModel
from vulnerabilities.models import VulnerabilityModel
from .models import ServiceModel
from .serializers import ServiceSerializer
from .forms import ServiceForm, ServiceIDForm


PAGE_DEFAULT = 1
NUM_ENTRY_DEFAULT = 50


#
# APIGetServices get services from these params:
#   searchText: Search content
#   sortName: Name of column is applied sort
#   sortOrder: sort entry by order 'asc' or 'desc'
#   pageSize: number of entry per page
#   pageNumber: page number of curent view
#   hostID: host to be used to filter
#   vulnID: vuln to be used to filter

class APIGetServices(APIView):
    def get(self, request):
        # Advanced Filter
        if request.GET.get('hostID'):
            try:
                hostID = int(request.GET.get('hostID'))
            except ValueError:
                return Response({'status': -1, 'message': "hostID is not integer"})
            try:
                serviceObjs = HostModel.objects.get(pk=hostID).services.all()
            except HostModel.DoesNotExist:
                return Response({'status': -1, 'message': "Host is not existed"})
        elif request.GET.get('vulnID'):
            try:
                vulnID = int(request.GET.get('vulnID'))
            except ValueError:
                return Response({'status': -1, 'message': "vulnID is not integer"})
            try:
                serviceObjs = VulnerabilityModel.objects.get(pk=vulnID).service
            except VulnerabilityModel.DoesNotExist:
                return Response({'status': -1, 'message': "Vulnerability is not existed"})
            serviceSerializer = ServiceSerializer(serviceObjs, many=False)
            return Response({'status': 0, 'object': serviceSerializer.data})
        else:
            serviceObjs = ServiceModel.objects.all()

        # Filter by search keyword
        if request.GET.get('searchText'):
            search = request.GET.get('searchText')
            query = Q(name__icontains=search) | Q(port__icontains=search) | Q(description__icontains=search)
            serviceObjs = serviceObjs.filter(query)

        # get total
        numObject = serviceObjs.count()

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
        querySet = serviceObjs.order_by(sortString)

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
        dataSerialized = ServiceSerializer(dataPaged, many=True)
        data = dict()
        data["total"] = numObject
        data['rows'] = dataSerialized.data
        return Response({"status":0, "object":data})


#
# APIGetServicesByID get services from id
# return {'retVal': '-1'} if id not found
# return service object if it's success
#

class APIGetServicesByID(APIView):
    def get(self, request):
        if request.GET.get('id'):
            id = request.GET.get('id')
            try:
                retService = ServiceModel.objects.get(pk=id)
            except (ServiceModel.DoesNotExist, ValueError):
                return Response({'status': '-1', 'message': 'Value error',
                             'detail': {"id": [{"message": "ID is not integer", "code": "value error"}]}})
            dataSerialized = ServiceSerializer(retService, many=False)
            return Response(dataSerialized.data)
        else:
            return Response({'status': '-1', 'message': 'fields are required',
                             'detail': {"id": [{"message": "ID is required", "code": "required"}]}})


#
# APIAddService add new service
# return {'retVal': '-1'} if id not found
# return service object if it's success
#

class APIAddService(APIView):
    def post(self, request):
        serviceForm = ServiceForm(request.POST)
        if serviceForm.is_valid():
            entry = serviceForm.save(commit=False)
            entry.createBy = User.objects.get(pk=1)
            entry.save()
            dataSerialized = ServiceSerializer(entry, many=False)
            return Response({'status': '0', 'object': dataSerialized.data})
        else:
            return Response({'status': '-1', 'message': 'Form is invalid', 'detail': serviceForm.errors})


#
# APIDeleteService delete existing service
# return {'retVal': '-1'} if id not found
# return service object if it's success
#

class APIDeleteService(APIView):
    def post(self, request):
        serviceForm = ServiceIDForm(request.POST)
        if serviceForm.is_valid():
            successOnDelete = 0
            try:
                ids = serviceForm.data['id'].split(',')
            except MultiValueDictKeyError:
                return Response({'status': '-1',  'message': 'Fields are required', 'detail': {"id": [{"message": "ID is required", "code": "required"}]}})
            for rawID in ids:
                try:
                    id = int(rawID)
                except ValueError:
                    pass
                else:
                    try:
                        retService = ServiceModel.objects.get(pk=id)
                    except ServiceModel.DoesNotExist:
                        pass
                    else:
                        retService.delete()
                        successOnDelete = successOnDelete + 1
            if successOnDelete==1:
                return Response(
                    {'status': '0', 'message': '1 service is successfully deleted.', "numDelete": successOnDelete})
            else:
                return Response({'status': '0', 'message': '{} services are successfully deleted.'.format(successOnDelete), "numDelete":successOnDelete})
        else:
            return Response({'status': '-1', 'message': 'Form is invalid.', 'detail': {serviceForm.errors}})


#
# APIUpdateService delete existing service
# return {'notification': 'error_msg'} if id not found
# return service object if it's success
#

class APIUpdateService(APIView):
    def post(self, request):
        if request.POST.get('id'):
            try:
                id = int(request.POST.get('id'))
            except ValueError:
                return Response({'status': '-1', 'message': 'Value error',
                                 'detail': {"id": [{"message": "ID is not integer", "code": "value error"}]}})
            serviceObj = ServiceModel.objects.get(pk=id)
            serviceForm = ServiceForm(request.POST, instance=serviceObj)
        else:
            return Response({'status': '-1', 'message': 'Fields are required',
                             'detail': {"id": [{"message": "ID is required", "code": "required"}]}})
        if serviceForm.is_valid():
            entry = serviceForm.save()
            dataSerialized = ServiceSerializer(entry, many=False)
            return Response({'status': '0', 'object': dataSerialized.data})
        else:
            return Response({'status': '-1', 'message': 'Form is invalid', 'detail': serviceForm.errors})