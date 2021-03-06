from django.utils.datastructures import MultiValueDictKeyError
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.contrib.auth.models import User
from hosts.models import HostModel
from vulnerabilities.models import VulnerabilityModel
from scans.models import ScanTaskModel, ScanInfoModel
from projects.models import ScanProjectModel
from .models import ServiceModel
from .serializers import ServiceSerializer
from .forms import ServiceForm, ServiceIDForm
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required
from .ultil import GetServices, GetServicesVuln

PAGE_DEFAULT = 1
NUM_ENTRY_DEFAULT = 50

#   APIGetServiceName get service name from id
#   Params: (id)
class APIGetServiceName(APIView):

    @method_decorator(permission_required('services.view_servicemodel', raise_exception=True))
    def get(self, request):
        if request.GET.get('id'):
            try:
                id = int(request.GET.get('id'))
            except (ValueError, TypeError):
                return Response({'status': '-1', 'message': 'Value error',
                                 'detail': {"id": [{"message": "ID is not integer", "code": "value error"}]}})
            try:
                name = ServiceModel.objects.get(pk=id).name
            except ServiceModel.DoesNotExist:
                return Response({'status': '-1', 'message': 'Vuln does not exist'})
            return Response({'status': 0, 'object': name})
        else:
            return Response({'status': '-1', 'message': 'fields are required',
                             'detail': {"id": [{"message": "ID is required", "code": "required"}]}})


# APIGetServices get services:
#   Params: (
#               Object Filter: [projectID], [scanID], [hostID], [vulnID], [serviceID],
#               Content Filter: [searchText], [sortOrder], [sortName], [pageSize], [pageNumber])
class APIGetServices(APIView):

    @method_decorator(permission_required('services.view_servicemodel', raise_exception=True))
    def get(self, request):
        kwarguments = dict()
        for kw in request.GET:
            kwarguments[kw] = request.GET.get(kw)
        retval = GetServices(**kwarguments)
        if retval['status'] != 0:
            return Response(retval)
        services = retval['object']

        # get total
        numObject = services.count()

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
        querySet = services.order_by(sortString)

        # Get Page Number
        if request.GET.get('pageNumber'):
            page = request.GET.get('pageNumber')
        else:
            page = PAGE_DEFAULT

        # Get Page Size
        if request.GET.get('pageSize'):
            numEntry = request.GET.get('pageSize')
            # IF Page size is 'ALL'
            if numEntry.lower() == 'all' or numEntry == '-1':
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


#   APIGetServicesByID get service from id
#   Params: (id)
class APIGetServicesByID(APIView):

    @method_decorator(permission_required('services.view_servicemodel', raise_exception=True))
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


# APIAddService add new service
class APIAddService(APIView):

    @method_decorator(permission_required('services.add_servicemodel', raise_exception=True))
    def post(self, request):
        serviceForm = ServiceForm(request.POST)
        if serviceForm.is_valid():
            entry = serviceForm.save(commit=False)
            entry.createBy = User.objects.get(username=request.user)
            entry.save()
            dataSerialized = ServiceSerializer(entry, many=False)
            return Response({'status': '0', 'object': dataSerialized.data})
        else:
            return Response({'status': '-1', 'message': 'Form is invalid', 'detail': serviceForm.errors})


# APIDeleteService delete existing service
class APIDeleteService(APIView):

    @method_decorator(permission_required('services.delete_servicemodel', raise_exception=True))
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


# APIUpdateService delete existing service
class APIUpdateService(APIView):

    @method_decorator(permission_required('services.change_servicemodel', raise_exception=True))
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


class APIServicesVuln(APIView):

    @method_decorator(permission_required('services.view_servicemodel', raise_exception=True))
    def get(self, request):
        kwarguments = dict()
        for kw in request.GET:
            kwarguments[kw] = request.GET.get(kw)
        retval = GetServicesVuln(**kwarguments)
        if retval['status'] != 0:
            return Response(retval)
        servicesVuln = retval['object']
        servicesVuln = servicesVuln.filter(Q(high__gt=0)|Q(med__gt=0)|Q(low__gt=0)|Q(info__gt=0))

        numObject = servicesVuln.count()
        # Get Page Number
        if request.GET.get('pageNumber'):
            page = request.GET.get('pageNumber')
        else:
            page = PAGE_DEFAULT

        # Get Page Size
        if request.GET.get('pageSize'):
            numEntry = request.GET.get('pageSize')
            # IF Page size is 'ALL'
            if numEntry.lower() == 'all' or numEntry == '-1':
                numEntry = numObject
        else:
            numEntry = NUM_ENTRY_DEFAULT
        try:
            querySetPaged = Paginator(servicesVuln, int(numEntry))
        except (ValueError, TypeError) as e:
            return Response({'status': -1, 'message': str(e)})
        dataPaged = querySetPaged.get_page(page)

        data = dict()
        data["total"] = numObject
        data['rows'] = dataPaged.object_list
        return Response({"status": 0, "object": data})
