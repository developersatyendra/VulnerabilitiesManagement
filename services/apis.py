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
from .ultil import GetServices

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


class APIServiceVulnStatistic(APIView):

    @method_decorator(permission_required('services.view_servicemodel', raise_exception=True))
    def get(self, request):
        serviceIDs= None
        vulnIDs = None

        # scanID process
        if request.GET.get('scanID'):
            scanID = request.GET.get('scanID')
            try:
                scanTask = ScanTaskModel.objects.get(id=scanID)
                print(scanTask)
            except (ValueError, TypeError) as e:
                return Response({'status': '-1', 'message': 'Value error',
                                 'detail': {"scanID": [{"message": "ID is not integer", "code": "value error"}]}})
            except ScanTaskModel.DoesNotExist:
                return Response({'status': '-1', 'message': 'Scan not found error',
                                 'detail': {"scanID": [{"message": "Scan does not exist", "code": "exist error"}]}})

            vulnIDs = scanTask.ScanInfoScanTask.distinct().values_list('vulnFound', flat=True)

        # hostID process
        elif request.GET.get('hostID'):
            hostID = request.GET.get('hostID')
            try:
                host = HostModel.objects.get(id=hostID)
            except (ValueError, TypeError) as e:
                return Response({'status': '-1', 'message': 'Value error',
                                 'detail': {"hostID": [{"message": "ID is not integer", "code": "value error"}]}})
            except HostModel.DoesNotExist:
                return Response({'status': '-1', 'message': 'Host not found error',
                                 'detail': {"hostID": [{"message": "Host does not exist", "code": "exist error"}]}})
            vulnIDs = host.ScanInfoHost.distinct().values_list('vulnFound', flat=True)

        # projectID process
        elif request.GET.get('projectID'):
            projectID = request.GET.get('projectID')
            try:
                project = ScanProjectModel.objects.get(id=projectID)

            except (ValueError, TypeError) as e:
                return Response({'status': '-1', 'message': 'Value error',
                                 'detail': {"projectID": [{"message": "ID is not integer", "code": "value error"}]}})
            except ScanProjectModel.DoesNotExist:
                return Response({'status': '-1', 'message': 'Project not found error',
                                 'detail': {"projectID": [{"message": "Project does not exist", "code": "exist error"}]}})
            scanInfoID = project.ScanProjectScanTask.values_list('ScanInfoScanTask')
            scanInfo = ScanInfoModel.objects.filter(id__in=scanInfoID).distinct()
            vulnIDs = scanInfo.values_list('vulnFound', flat=True)

        if vulnIDs:
            vulnQuerySet = VulnerabilityModel.objects.filter(id__in=vulnIDs)
        else:
            vulnQuerySet = VulnerabilityModel.objects.all()
        if request.GET.get('topObj'):
            try:
                topObj = int(request.GET.get('topObj'))
            except (ValueError, TypeError) as e:
                return Response({'status': '-1', 'message': 'Value error',
                                 'detail': {"hostID": [{"message": "Top Obj is not integer", "code": "value error"}]}})
            statVals = vulnQuerySet.values('service').annotate(count=Count('service')).values('service__name',
                                                                                              'service__port',
                                                                                              'count').order_by(
                '-count')[:topObj]
        else:
            statVals = vulnQuerySet.values('service').annotate(count=Count('service')).values('service__name',
                                                                                              'service__port',
                                                                                              'count').order_by(
                '-count')
        object_data = []
        for statVal in statVals:
            object_data.append({'name': statVal['service__name'], 'port': statVal['service__port'], 'vuln': statVal['count']})
        return Response({'status': 0, 'object': object_data})