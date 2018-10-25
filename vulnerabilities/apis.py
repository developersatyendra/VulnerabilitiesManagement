from django.utils.datastructures import MultiValueDictKeyError
from rest_framework.views import APIView
from rest_framework.response import Response
from services.models import ServiceModel
from scans.models import ScanTaskModel
from .models import VulnerabilityModel
from .serializers import VulnSerializer
from .forms import VulnForm, VulnIDForm
from .ultil import GetVulns
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required

PAGE_DEFAULT = 1
NUM_ENTRY_DEFAULT = 50


######################################################
#   APIGetVulnName get Name of Vuln from id
#

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


######################################################
# APIGetVulns get vulns from these params:
#   searchText: Search content
#   sortName: Name of column is applied sort
#   sortOrder: sort entry by order 'asc' or 'desc'
#   pageSize: number of entry per page
#   pageNumber: page number of curent view
#   projectID: project to be used to filter
#   scanID: ScanTask to be used to filter
#   hostID: Vuln to be used to filter
#   serviceID: Service to be used to filter

class APIGetVulns(APIView):

    @method_decorator(permission_required('vulnerabilities.view_vulnerabilitymodel', raise_exception=True))
    def get(self, request):
        kw = dict(request.GET)
        retval = GetVulns(**kw)
        if retval['status'] != 0:
            return Response({'status': retval['status'], 'message': retval['message'], 'detail': retval['detail']})

        dataSerialized = VulnSerializer(retval['object'], many=True)
        data = dict()
        data["total"] = retval['total']
        data['rows'] = dataSerialized.data
        return Response({'status':0, 'object':data})


#
# APIGetVulnsByID get vulns from id
# return {'retVal': '-1'} if id not found
# return vuln object if it's success
#

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
# return {'retVal': '-1'} if id not found
# return Vuln object if it's success
#

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


#
# APIDeleteVuln delete existing vulnerability
# return {'retVal': '-1'} if id not found
# return {'retVal': 'Num of Success on Deleting'} if it's success
#

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


#
# APIUpdateVuln update vulnerability
# return {'notification': 'error_msg'} if id not found
# return Vuln object if it's success
#

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


#
# APIGetCurrentHostVuln get existing vulns on specific host:
#   search: Search content
#   sort: Name of column is applied sort
#   order: sort entry by order 'asc' or 'desc'
#   offset: number of entry per page
#   limit: page number of curent view

class APIGetCurrentHostVuln(APIView):

    @method_decorator(permission_required('vulnerabilities.view_vulnerabilitymodel', raise_exception=True))
    def get(self, request):
        if request.GET.get('id'):
            try:
                id = int(request.GET.get('id'))
            except TypeError:
                return Response({'status': '-1', 'message': 'Value error',
                                 'detail': {"id": [{"message": "ID is not integer", "code": "value error"}]}})
            scanTask = ScanTaskModel.objects.filter(ScanInfoScanTask__hostScanned=id).order_by('-startTime')[0]
            retval = GetVulns(scanID=scanTask.id, hostID=id, **dict(request.GET))
            if retval['status'] != 0:
                return Response({'status': retval['status'], 'message': retval['message'], 'detail': retval['detail']})
            dataSerialized = VulnSerializer(retval['object'], many=True)
            data = dict()
            data["total"] = retval['total']
            data['rows'] = dataSerialized.data
            return Response({'status': 0, 'object': data})
        else:
            return Response({'status': '-1', 'message': 'fields are required',
                             'detail': {"id": [{"message": "ID is required", "code": "required"}]}})