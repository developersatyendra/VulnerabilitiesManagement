from django.utils.datastructures import MultiValueDictKeyError
from rest_framework.views import APIView
from rest_framework.response import Response
from services.models import ServiceModel
from django.db.models import Q, Max
from scans.models import ScanTaskModel, ScanInfoModel
from hosts.models import HostModel
from django.core.paginator import Paginator
from .models import VulnerabilityModel
from .serializers import VulnSerializer
from .forms import VulnForm, VulnIDForm
from .ultil import GetVulns, GetCurrentHostVuln, GetCurrentProjectVuln, GetCurrentGobalVuln
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required

PAGE_DEFAULT = 1
NUM_ENTRY_DEFAULT = 50


#   APIGetVulnName get vulnerability name from id
#   Params: (id)
class APIGetVulnName(APIView):

    @method_decorator(permission_required('vulnerabilities.view_vulnerabilitymodel', raise_exception=True))
    def get(self, request):
        if request.GET.get('id'):
            try:
                id = int(request.GET.get('id'))
            except (ValueError, TypeError):
                return Response({'status': '-1', 'message': 'Value error',
                                 'detail': {"id": [{"message": "ID is not integer", "code": "value error"}]}})
            try:
                name = VulnerabilityModel.objects.get(pk=id).name
            except VulnerabilityModel.DoesNotExist:
                return Response({'status': '-1', 'message': 'Vuln does not exist'})
            return Response({'status': 0, 'object': name})
        else:
            return Response({'status': '-1', 'message': 'fields are required',
                             'detail': {"id": [{"message": "ID is required", "code": "required"}]}})


# APIGetVulns get vulns
class APIGetVulns(APIView):

    @method_decorator(permission_required('vulnerabilities.view_vulnerabilitymodel', raise_exception=True))
    def get(self, request):
        kwarguments = dict()
        for kw in request.GET:
            kwarguments[kw] = request.GET.get(kw)
        retval = GetVulns(**kwarguments)
        if retval['status'] != 0:
            return Response({'status': retval['status'], 'message': retval['message']})
        vulns = retval['object']
        searchText = request.GET.get('searchText', None)
        if searchText:
            querySearch = Q(description__icontains=search) \
                             | Q(name__icontains=search) \
                             | Q(observation__icontains=search) \
                             | Q(recommendation__icontains=search) \
                             | Q(cve__icontains=search) \
                             | Q(levelRisk__icontains=search) \
                             | Q(service__name__icontains=search)
            vulns = vulns.filter(querySearch)
        numObject = vulns.count()

        # Get sort order
        if request.GET.get('sortOrder') == 'asc':
            sortString = ''
        else:
            sortString = '-'

        # Get sort filed
        if request.GET.get('sortName'):
            sortString = sortString + request.GET.get('sortName')
        else:
            sortString = sortString + 'levelRisk'
        vulns = vulns.order_by(sortString)

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
            querySetPaged = Paginator(vulns, int(numEntry))
        except (ValueError, TypeError) as e:
            return Response({'status': -1, 'message': str(e)})
        dataPaged = querySetPaged.get_page(page)
        dataSerialized = VulnSerializer(dataPaged, many=True)
        data = dict()
        data["total"] = numObject
        data['rows'] = dataSerialized.data
        return Response({'status':0, 'object':data})


# APIGetVulnsByID get vulns from id
#   Params: (id)
class APIGetVulnByID(APIView):

    @method_decorator(permission_required('vulnerabilities.view_vulnerabilitymodel', raise_exception=True))
    def get(self, request):
        if request.GET.get('id'):
            id = request.GET.get('id')
            try:
                retService = VulnerabilityModel.objects.get(pk=id)
            except ValueError:
                return Response({'status': '-1', 'message': 'Value error',
                                 'detail': {"id": [{"message": "ID is not integer", "code": "value error"}]}})
            except VulnerabilityModel.DoesNotExist:
                return Response({'status': '-1', 'message': 'Vuln ID does not exist',
                                 'detail': {}})
            dataSerialized = VulnSerializer(retService, many=False)
            return Response(dataSerialized.data)
        else:
            return Response({'status': '-1', 'message': 'fields are required',
                             'detail': {"id": [{"message": "ID is required", "code": "required"}]}})


# APIAddVuln add new Vulnerability
class APIAddVuln(APIView):

    @method_decorator(permission_required('vulnerabilities.add_vulnerabilitymodel', raise_exception=True))
    def post(self, request):
        vulnForm = VulnForm(request.POST)
        if vulnForm.is_valid():
            vulnObj = vulnForm.save(commit=True)
            dataSerialized = VulnSerializer(vulnObj, many=False)
            return Response({'status': '0', 'object': dataSerialized.data})
        else:
            return Response({'status': '-1', 'message': 'Form is invalid', 'detail': vulnForm.errors})


# APIDeleteVuln delete existing vulnerability
class APIDeleteVuln(APIView):

    @method_decorator(permission_required('vulnerabilities.delete_vulnerabilitymodel', raise_exception=True))
    def post(self, request):
        vulnForm = VulnIDForm(request.POST)
        if vulnForm.is_valid():
            successOnDelete = 0
            try:
                ids = vulnForm.data['id'].split(',')
            except MultiValueDictKeyError:
                return Response({'status': '-1',  'message': 'Fields are required', 'detail': {"id": [{"message": "ID is required", "code": "required"}]}})
            for rawID in ids:
                try:
                    id = int(rawID)
                except ValueError:
                    pass
                else:
                    try:
                        retVuln = VulnerabilityModel.objects.get(pk=id)
                    except ServiceModel.DoesNotExist:
                        pass
                    else:
                        retVuln.delete()
                        successOnDelete = successOnDelete + 1
            if successOnDelete==1:
                return Response(
                            {'status': '0', 'message': '1 Vulnerability is successfully deleted.'})
            else:
                return Response(
                {'status': '0', 'message': '{} Vulnerabilities are successfully deleted.'.format(successOnDelete), 'numDeleted': successOnDelete})
        else:
            return Response({'status': '-1', 'message': 'Form is invalid', 'detail': {vulnForm.errors}})


# APIUpdateVuln update vulnerability
class APIUpdateVuln(APIView):

    @method_decorator(permission_required('vulnerabilities.change_vulnerabilitymodel', raise_exception=True))
    def post(self, request):
        if request.POST.get('id'):
            try:
                id = int(request.POST.get('id'))
            except ValueError:
                return Response({'status': '-1', 'message': 'Value error',
                                 'detail': {"id": [{"message": "ID is not integer", "code": "value error"}]}})
            vulnObj = VulnerabilityModel.objects.get(pk=id)
            vulnForm = VulnForm(request.POST, instance=vulnObj)
        else:
            return Response({'status': '-1', 'message': 'Fields are required',
                             'detail': {"id": [{"message": "ID is required", "code": "required"}]}})
        if vulnForm.is_valid():
            entry = vulnForm.save()
            dataSerialized = VulnSerializer(entry, many=False)
            return Response({'status': '0', 'object': dataSerialized.data})
        else:
            return Response({'status': '-1', 'message': 'Form is invalid', 'detail': vulnForm.errors})


# APIGetCurrentHostVuln get existing vulns on specific host:
class APIGetCurrentHostVuln(APIView):

    @method_decorator(permission_required('vulnerabilities.view_vulnerabilitymodel', raise_exception=True))
    def get(self, request):
        kwarguments = dict()
        for kw in request.GET:
            kwarguments[kw] = request.GET.get(kw)
        retval = GetCurrentHostVuln(**kwarguments)
        if retval['status'] != 0:
            return Response({'status': retval['status'], 'message': retval['message']})
        vulns = retval['object']
        searchText = request.GET.get('searchText', None)
        if searchText:
            querySearch = Q(description__icontains=search) \
                          | Q(name__icontains=search) \
                          | Q(observation__icontains=search) \
                          | Q(recommendation__icontains=search) \
                          | Q(cve__icontains=search) \
                          | Q(levelRisk__icontains=search) \
                          | Q(service__name__icontains=search)
            vulns = vulns.filter(querySearch)
        numObject = vulns.count()

        # Get sort order
        if request.GET.get('sortOrder') == 'asc':
            sortString = ''
        else:
            sortString = '-'

        # Get sort filed
        if request.GET.get('sortName'):
            sortString = sortString + request.GET.get('sortName')
        else:
            sortString = sortString + 'levelRisk'
        vulns = vulns.order_by(sortString)

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
            querySetPaged = Paginator(vulns, int(numEntry))
        except (ValueError, TypeError) as e:
            return Response({'status': -1, 'message': str(e)})
        dataPaged = querySetPaged.get_page(page)
        dataSerialized = VulnSerializer(dataPaged, many=True)
        data = dict()
        data["total"] = numObject
        data['rows'] = dataSerialized.data
        return Response({'status': 0, 'object': data})


# APIGetCurrentProjectVuln get existing vulns on specific project:
class APIGetCurrentProjectVuln(APIView):

    @method_decorator(permission_required('vulnerabilities.view_vulnerabilitymodel', raise_exception=True))
    def get(self, request):
        kwarguments = dict()
        for kw in request.GET:
            kwarguments[kw] = request.GET.get(kw)
        retval = GetCurrentProjectVuln(**kwarguments)
        if retval['status'] != 0:
            return Response({'status': retval['status'], 'message': retval['message']})
        vulns = retval['object']
        searchText = request.GET.get('searchText', None)
        if searchText:
            querySearch = Q(description__icontains=search) \
                          | Q(name__icontains=search) \
                          | Q(observation__icontains=search) \
                          | Q(recommendation__icontains=search) \
                          | Q(cve__icontains=search) \
                          | Q(levelRisk__icontains=search) \
                          | Q(service__name__icontains=search)
            vulns = vulns.filter(querySearch)
        numObject = vulns.count()

        # Get sort order
        if request.GET.get('sortOrder') == 'asc':
            sortString = ''
        else:
            sortString = '-'

        # Get sort filed
        if request.GET.get('sortName'):
            sortString = sortString + request.GET.get('sortName')
        else:
            sortString = sortString + 'levelRisk'
        vulns = vulns.order_by(sortString)

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
            querySetPaged = Paginator(vulns, int(numEntry))
        except (ValueError, TypeError) as e:
            return Response({'status': -1, 'message': str(e)})
        dataPaged = querySetPaged.get_page(page)
        dataSerialized = VulnSerializer(dataPaged, many=True)
        data = dict()
        data["total"] = numObject
        data['rows'] = dataSerialized.data
        return Response({'status': 0, 'object': data})


# APIGetCurrentProjectVuln get existing vulns on specific project:
class APIGetCurrentGlobalVuln(APIView):

    @method_decorator(permission_required('vulnerabilities.view_vulnerabilitymodel', raise_exception=True))
    def get(self, request):
        kwarguments = dict()
        for kw in request.GET:
            kwarguments[kw] = request.GET.get(kw)
        retval = GetCurrentGobalVuln(**kwarguments)
        if retval['status'] != 0:
            return Response({'status': retval['status'], 'message': retval['message']})
        vulns = retval['object']
        searchText = request.GET.get('searchText', None)
        if searchText:
            querySearch = Q(description__icontains=search) \
                          | Q(name__icontains=search) \
                          | Q(observation__icontains=search) \
                          | Q(recommendation__icontains=search) \
                          | Q(cve__icontains=search) \
                          | Q(levelRisk__icontains=search) \
                          | Q(service__name__icontains=search)
            vulns = vulns.filter(querySearch)
        numObject = vulns.count()

        # Get sort order
        if request.GET.get('sortOrder') == 'asc':
            sortString = ''
        else:
            sortString = '-'

        # Get sort filed
        if request.GET.get('sortName'):
            sortString = sortString + request.GET.get('sortName')
        else:
            sortString = sortString + 'levelRisk'
        vulns = vulns.order_by(sortString)

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
            querySetPaged = Paginator(vulns, int(numEntry))
        except (ValueError, TypeError) as e:
            return Response({'status': -1, 'message': str(e)})
        dataPaged = querySetPaged.get_page(page)
        dataSerialized = VulnSerializer(dataPaged, many=True)
        data = dict()
        data["total"] = numObject
        data['rows'] = dataSerialized.data
        return Response({'status': 0, 'object': data})