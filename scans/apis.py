from django.utils.datastructures import MultiValueDictKeyError
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.contrib.auth.models import User
from .ultil import GetScansVuln, GetScans
from .models import ScanTaskModel
from .serializers import ScanSerializer, ScanAttachmentSerializer, ScanVulnSerializer
from .forms import ScanIDForm, ScanAttachmentForm, ScanAddForm
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
from os import remove as RemoveFile
from datetime import datetime, timedelta
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required
from django.conf import settings

PAGE_DEFAULT = 1
NUM_ENTRY_DEFAULT = 50


#   APIGetScanName get scan name from id
#   Params: (id)
class APIGetScanName(APIView):

    @method_decorator(permission_required('scans.view_scantaskmodel', raise_exception=True))
    def get(self, request):
        if request.GET.get('id'):
            try:
                id = int(request.GET.get('id'))
            except (ValueError, TypeError):
                return Response({'status': '-1', 'message': 'Value error',
                                 'detail': {"id": [{"message": "ID is not integer", "code": "value error"}]}})
            try:
                name = ScanTaskModel.objects.get(pk=id).name
            except ScanTaskModel.DoesNotExist:
                return Response({'status': '-1', 'message': 'Scan does not exist'})
            return Response({'status': 0, 'object':name})
        else:
            return Response({'status': '-1', 'message': 'fields are required',
                             'detail': {"id": [{"message": "ID is required", "code": "required"}]}})


# APIGetHostsVuln get scans and number of vulnerability [H, M, L, I]:
#   Params: (
#               Object Filter: [projectID], [scanID], [hostID], [vulnID], [serviceID],
#               Content Filter: [searchText], [sortOrder], [sortName], [pageSize], [pageNumber])
class APIGetScansVuln(APIView):

    @method_decorator(permission_required('scans.view_scantaskmodel', raise_exception=True))
    def get(self, request):
        kwarguments = dict()
        for kw in request.GET:
            kwarguments[kw] = request.GET.get(kw)
        retval = GetScansVuln(**kwarguments)
        if retval['status'] != 0:
            return Response(retval)
        scans = retval['object']

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
                numEntry = scans.count()
        else:
            numEntry = NUM_ENTRY_DEFAULT
        try:
            querySetPaged = Paginator(scans, int(numEntry))
        except (ValueError, TypeError) as e:
            return Response({'status': -1, 'message': str(e)})
        dataPaged = querySetPaged.get_page(page)
        dataSerialized = ScanVulnSerializer(dataPaged, many=True)

        object = {
            'total': retval['total'],
            'rows': dataSerialized.data
        }
        return Response({'status': 0, 'object': object})


# APIGetScans get scans from these params:
#   Params: (
#               Object Filter: [projectID], [scanID], [hostID], [vulnID], [serviceID],
#               Content Filter: [searchText], [sortOrder], [sortName], [pageSize], [pageNumber])
class APIGetScans(APIView):

    @method_decorator(permission_required('scans.view_scantaskmodel', raise_exception=True))
    def get(self, request):
        kwarguments = dict()
        for kw in request.GET:
            kwarguments[kw] = request.GET.get(kw)
        retval = GetScansVuln(**kwarguments)
        if retval['status'] != 0:
            return Response(retval)

        # Get object
        scanTask = retval['object'].distinct()

        numObject = scanTask.count()

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
        sortString = sortString.replace('.', '__')
        scanTask = scanTask.order_by(sortString)

        # Get Page Number
        if request.GET.get('pageNumber'):
            try:
                page = int(request.GET.get('pageNumber'))
            except ValueError:
                page = PAGE_DEFAULT
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
        querySetPaged = Paginator(scanTask, int(numEntry))
        dataPaged = querySetPaged.get_page(page)
        dataSerialized = ScanSerializer(dataPaged, many=True)
        data = dict()
        data["total"] = numObject
        data['rows'] = dataSerialized.data
        return Response({'status': 0, 'object': data})


#   APIGetScanByID get scan from id
#   Params: (id)
class APIGetScanByID(APIView):

    @method_decorator(permission_required('scans.view_scantaskmodel', raise_exception=True))
    def get(self, request):
        if request.GET.get('id'):
            id = request.GET.get('id')
            try:
                retService = ScanTaskModel.objects.get(pk=id)
            except ValueError:
                return Response({'status': '-1', 'message': 'Value error',
                                 'detail': {"id": [{"message": "ID is not integer", "code": "value error"}]}})
            except ScanTaskModel.DoesNotExist:
                return Response({'status': '-1', 'message': 'Vuln ID does not exist',
                                 'detail': {}})
            dataSerialized = ScanSerializer(retService, many=False)
            return Response(dataSerialized.data)
        else:
            return Response({'status': '-1', 'message': 'fields are required',
                             'detail': {"id": [{"message": "ID is required", "code": "required"}]}})


# APIAddScan add new Scantask
class APIAddScan(APIView):
    @method_decorator(permission_required('scans.add_scantaskmodel', raise_exception=True))
    def post(self, request, format=None):
        scanAddForm = ScanAddForm(request.POST)
        if scanAddForm.is_valid():
            scanObj = scanAddForm.save(commit=False)
            scanObj.scanBy = User.objects.get(username=request.user)
            scanObj.submitter = User.objects.get(pk=1)
            # scanObj.fileAttachment = request.FILES['fileAttachment']
            scanObj.save()
            dataSerialized = ScanSerializer(scanObj, many=False)
            return Response({'status': '0', 'object': dataSerialized.data})
        else:
            return Response({'status': '-1', 'message': 'Form is invalid', 'detail': scanAddForm.errors})


# APIDeleteScan delete existing Scan Tasks
class APIDeleteScan(APIView):

    @method_decorator(permission_required('scans.delete_scantaskmodel', raise_exception=True))
    def post(self, request):
        print(request.POST)
        scanForm = ScanIDForm(request.POST)
        if scanForm.is_valid():
            successOnDelete = 0
            try:
                ids = scanForm.data['id'].split(',')
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
                        scanTask = ScanTaskModel.objects.get(pk=id)
                    except ScanTaskModel.DoesNotExist:
                        pass
                    else:
                        scanTask.delete()
                        successOnDelete = successOnDelete + 1
            if successOnDelete==1:
                return Response(
                    {'status': '0', 'message': '1 Scanning Task is successfully deleted.', 'numDeleted':successOnDelete})
            else:
                return Response(
                {'status': '0', 'message': '{} Scanning Tasks are successfully deleted.'.format(successOnDelete), 'numDeleted': successOnDelete})
        else:
            return Response({'status': '-1', 'message': 'Form is invalid', 'detail': {scanForm.errors}})


# APIUpdateScan update Scan Tasks
class APIUpdateScan(APIView):

    @method_decorator(permission_required('scans.change_scantaskmodel', raise_exception=True))
    def post(self, request):
        print(request.POST)
        if request.POST.get('id'):
            try:
                id = int(request.POST.get('id'))
            except ValueError:
                return Response({'status': '-1', 'message': 'Value error',
                                 'detail': {"id": [{"message": "ID is not integer", "code": "value error"}]}})
            scanObj = ScanTaskModel.objects.get(pk=id)
            scanAddForm = ScanAddForm(request.POST, instance=scanObj)
        else:
            return Response({'status': '-1', 'message': 'Fields are required',
                             'detail': {"id": [{"message": "ID is required", "code": "required"}]}})
        if scanAddForm.is_valid():
            entry = scanAddForm.save()
            dataSerialized = ScanSerializer(entry, many=False)
            return Response({'status': '0', 'object': dataSerialized.data})
        else:
            return Response({'status': '-1', 'message': 'Form is invalid', 'detail': scanAddForm.errors})



# Get attachment of Scan Task
class APIGetScanAttachment(APIView):

    @method_decorator(permission_required('scans.view_scantaskmodel', raise_exception=True))
    def get(self, request):
        if request.GET.get('id'):
            id = request.GET.get('id')
            try:
                retService = ScanTaskModel.objects.get(pk=id)
            except TypeError:
                return Response({'status': '-1', 'message': 'Value error',
                                 'detail': {"id": [{"message": "ID is not integer", "code": "value error"}]}})
            except ScanTaskModel.DoesNotExist:
                return Response({'status': '-1', 'message': 'Vuln ID does not exist',
                                 'detail': {}})
            dataSerialized = ScanAttachmentSerializer(retService, many=False)
            return Response(dataSerialized.data)
        else:
            return Response({'status': '-1', 'message': 'fields are required',
                             'detail': {"id": [{"message": "ID is required", "code": "required"}]}})


# Add attachment update Scan Tasks
class APIAddAttachment(APIView):
    parser_classes = (MultiPartParser, FormParser, FileUploadParser,)

    @method_decorator(permission_required('scans.change_scantaskmodel', raise_exception=True))
    def post(self, request):
        if request.POST.get('id'):
            try:
                id = int(request.POST.get('id'))
            except ValueError:
                return Response({'status': '-1', 'message': 'Value error',
                                 'detail': {"id": [{"message": "ID is not integer", "code": "value error"}]}})
            try:
                scanObj = ScanTaskModel.objects.get(pk=id)
                if(scanObj.fileAttachment):
                    try:
                        RemoveFile(scanObj.fileAttachment.path)
                    except FileNotFoundError:
                        pass
            except ScanTaskModel.DoesNotExist:
                return Response({'status': '-1', 'message': 'Vuln ID does not exist',
                                 'detail': {}})
            scanForm = ScanAttachmentForm(request.POST, request.FILES, instance=scanObj)
        else:
            return Response({'status': '-1', 'message': 'Fields are required',
                             'detail': {"id": [{"message": "ID is required", "code": "required"}]}})
        if scanForm.is_valid():
            entry = scanForm.save()
            dataSerialized = ScanSerializer(entry, many=False)
            return Response({'status': '0', 'object': dataSerialized.data})
        else:
            return Response({'status': '-1', 'message': 'Form is invalid', 'detail': scanForm.errors})


# Delete attachment update Scan Tasks
class APIDeleteAttachment(APIView):

    @method_decorator(permission_required('scans.delete_scantaskmodel', raise_exception=True))
    def post(self, request):
        if request.POST.get('id'):
            try:
                id = int(request.POST.get('id'))
            except ValueError:
                return Response({'status': '-1', 'message': 'Value error',
                                 'detail': {"id": [{"message": "ID is not integer", "code": "value error"}]}})
            try:
                scanObj = ScanTaskModel.objects.get(pk=id)
            except ScanTaskModel.DoesNotExist:
                return Response({'status': '-1', 'message': 'Vuln ID does not exist',
                                 'detail': {}})
            if scanObj.fileAttachment:
                RemoveFile(scanObj.fileAttachment.path)
                scanObj.fileAttachment = None
                scanObj.save()
                return Response({'status': '0', 'message': 'Attachment is deleted successfully'})
            return Response({'status': '-1', 'message': 'Scan Task does not have attachment'})
        else:
            return Response({'status': '-1', 'message': 'Fields are required',
                             'detail': {"id": [{"message": "ID is required", "code": "required"}]}})

