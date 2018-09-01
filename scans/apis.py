from django.utils.datastructures import MultiValueDictKeyError
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.contrib.auth.models import User
from .models import ScanTaskModel
from .serializers import ScanSerializer, ScanAttachmentSerializer, ScanVulnSerializer
from .forms import ScanIDForm, ScanAttachmentForm, ScanAddForm
from projects.models import ScanProjectModel
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
from os import remove as RemoveFile
from datetime import datetime, timedelta

PAGE_DEFAULT = 1
NUM_ENTRY_DEFAULT = 50

# High is >= LEVEL_HIGH
LEVEL_HIGH = 7

# Med is >= LEVEL_MED AND < LEVEL_HIGH
LEVEL_MED = 4

# Low is > LEVEL_INFO AND < LEVEL_MED
# Info is = LEVEL_INFO
LEVEL_INFO = 0

######################################################
#   APIGetScansVuln get scan with vulnerabilities from these params:
#   searchText: Search content
#   sortName: Name of column is applied sort
#   sortOrder: sort entry by order 'asc' or 'desc'
#   pageSize: number of entry per page
#   pageNumber: page number of curent view
#   projectID: project to be used to filter
#   hostID: host to be used to filter
#   vulnID: vuln to be used to filter
#   dayRange: range of day to filter

class APIGetScansVuln(APIView):
    def get(self, request):
        scanTask = ScanTaskModel.objects.all()

        ######################################################
        # Adv Filter
        #
        # Filter by project
        query = Q()
        if request.GET.get('projectID'):
            try:
                projectID = int(request.GET.get('projectID'))
            except ValueError:
                return Response({'status': -1, 'message': "projectID is not integer"})
            scanTask = scanTask.filter(scanProject=projectID)

        # Filter by host
        if request.GET.get('hostID'):
            try:
                hostID = int(request.GET.get('hostID'))
            except ValueError:
                return Response({'status': -1, 'message': "hostID is not integer"})
            scanTask = scanTask.filter(scanInfo__hostScanned__id=hostID)

        # Filter by vuln
        if request.GET.get('vulnID'):
            try:
                vulnID = int(request.GET.get('vulnID'))
            except ValueError:
                return Response({'status': -1, 'message': "vulnID is not integer"})
            scanTask = scanTask.filter(scanInfo__vulnFound__id=vulnID)

        scanTask =  scanTask.annotate(
                high=Count('scanInfo__vulnFound', filter=Q(scanInfo__vulnFound__levelRisk__gte=LEVEL_HIGH), distinct=True),
                med=Count('scanInfo__vulnFound', filter=(Q(scanInfo__vulnFound__levelRisk__gte=LEVEL_MED)&Q(scanInfo__vulnFound__levelRisk__lt=LEVEL_HIGH)),distinct=True),
                low=Count('scanInfo__vulnFound', filter=Q(scanInfo__vulnFound__levelRisk__gt=LEVEL_INFO)&Q(scanInfo__vulnFound__levelRisk__lt=LEVEL_MED), distinct=True),
                info=Count('scanInfo__vulnFound', filter=Q(scanInfo__vulnFound__levelRisk=LEVEL_INFO), distinct=True),
                numHost=Count('scanInfo', distinct=True))

        ######################################################
        # Filter by day range
        #
        if request.GET.get('dayRange'):
            try:
                dayRange = int(request.GET.get('dayRange'))
            except ValueError:
                return Response({'status': -1, 'message': "dayRange is not integer"})
            filterDate = (datetime.now() - timedelta(days=dayRange)).date()
            scanTask = scanTask.filter(startTime__gte=filterDate)
        ######################################################
        # Filter by search keyword
        #
        if request.GET.get('searchText'):
            search = request.GET.get('searchText')
            query = Q(name__icontains=search) | \
                    Q(startTime__icontains=search) | \
                    Q(endTime__icontains=search)
            scanTask = scanTask.filter(query)

        # Set filter to get distinct entry only
        scanTask = scanTask.distinct()

        # Get number of object
        numObject = scanTask.count()

        # Get sort order
        if request.GET.get('order') == 'asc':
            sortString = ''
        else:
            sortString = '-'

        # Get sort filed
        if request.GET.get('sort'):
            sortString = sortString + request.GET.get('sort')
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
            if numEntry.lower() == 'all' or numEntry == -1:
                numEntry = numObject
        else:
            numEntry = NUM_ENTRY_DEFAULT
        querySetPaged = Paginator(scanTask, int(numEntry))
        dataPaged = querySetPaged.get_page(page)
        dataSerialized = ScanVulnSerializer(dataPaged, many=True)
        data = dict()
        data["total"] = numObject
        data['rows'] = dataSerialized.data
        return Response({'status': 0, 'object': data})


######################################################
#   APIGetScans get scan task from these params:
#   searchText: Search content
#   sortName: Name of column is applied sort
#   sortOrder: sort entry by order 'asc' or 'desc'
#   pageSize: number of entry per page
#   pageNumber: page number of curent view
#   projectID: project to be used to filter
#   hostID: host to be used to filter
#   vulnID: vuln to be used to filter
#   dayRange: range of day to filter

class APIGetScans(APIView):
    def get(self, request):
        scanTask = ScanTaskModel.objects.all()

        ######################################################
        # Adv Filter
        #
        # Filter by project
        if request.GET.get('projectID'):
            try:
                projectID = int(request.GET.get('projectID'))
            except ValueError:
                return Response({'status': -1, 'message': "projectID is not integer"})
            scanTask = scanTask.filter(scanProject=projectID)

        # Filter by host
        if request.GET.get('hostID'):
            try:
                hostID = int(request.GET.get('hostID'))
            except ValueError:
                return Response({'status': -1, 'message': "hostID is not integer"})
            scanTask = scanTask.filter(scanInfo__hostScanned__id=hostID)

        # Filter by vuln
        if request.GET.get('vulnID'):
            try:
                vulnID = int(request.GET.get('vulnID'))
            except ValueError:
                return Response({'status': -1, 'message': "vulnID is not integer"})
            scanTask = scanTask.filter(scanInfo__vulnFound__id=vulnID)
        ######################################################
        # Filter by day range
        #
        if request.GET.get('dayRange'):
            try:
                dayRange = int(request.GET.get('dayRange'))
            except ValueError:
                return Response({'status': -1, 'message': "dayRange is not integer"})
            filterDate = (datetime.now() - timedelta(days=dayRange)).date()
            scanTask = scanTask.filter(startTime__gte=filterDate)

        ######################################################
        # Filter by search keyword
        #
        if request.GET.get('searchText'):
            search = request.GET.get('searchText')
            searchQuery = Q(name__icontains=search) | \
                    Q(startTime__icontains=search) | \
                    Q(endTime__icontains=search)
            scanTask = scanTask.filter(searchQuery)

        # Set filter to get distinct entry only
        scanTask = scanTask.distinct()

        # Get number of object
        numObject = scanTask.count()

        # Get sort order
        if request.GET.get('order') == 'asc':
            sortString = ''
        else:
            sortString = '-'

        # Get sort filed
        if request.GET.get('sort'):
            sortString = sortString + request.GET.get('sort')
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
            if numEntry.lower() == 'all' or numEntry == -1:
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


# ######################################################
# #   APIGetScans get scan from these params:
# #   searchText: Search content
# #   sortName: Name of column is applied sort
# #   sortOrder: sort entry by order 'asc' or 'desc'
# #   pageSize: number of entry per page
# #   pageNumber: page number of curent view
# #   advFilter: "projectID", "hostID", "vulnID"
# #   advFilterValue: Value to be used to filter
# class APIGetScans(APIView):
#     def get(self, request):
#         # Filter by search keyword
#         if request.GET.get('searchText'):
#             search = request.GET.get('searchText')
#             # Query on Projects Model
#             queryProjectModel = Q(name__icontains=search)
#             projectPK = ScanProjectModel.objects.filter(queryProjectModel).values_list('pk', flat=True)
#
#             # Query on ScanTask
#             query = Q(name__icontains=search) |\
#                     Q(scanProject__in=projectPK) | \
#                     Q(description__icontains=search)
#             querySet = ScanTaskModel.objects.filter(query)
#         else:
#             querySet = ScanTaskModel.objects.all()
#
#         # Adv Filter
#         if request.GET.get('advFilter') and request.GET.get('advFilterValue'):
#             advFilter=request.GET.get('advFilter')
#             advFilterValue=request.GET.get('advFilterValue')
#
#             # if advFilter is projectID
#             queryAdv = None
#             if advFilter=='projectID':
#                 queryAdv = Q(scanProject__id__iexact=advFilterValue)
#             elif advFilter=='hostID':
#                 queryAdv = Q(scanInfo__hostScanned__id__iexact=advFilterValue)
#             elif advFilter=='vulnID':
#                 queryAdv = Q(scanInfo__vulnFound__id__iexact=advFilterValue)
#             if queryAdv:
#                 querySet = querySet.filter(queryAdv)
#
#         # Get number of object
#         numObject = querySet.count()
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
#         sortString = sortString.replace('.', '__')
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
#         dataSerialized = ScanSerializer(dataPaged, many=True)
#         data = dict()
#         data["total"] = numObject
#         data['rows'] = dataSerialized.data
#         return Response({'status': 0, 'object': data})


######################################################
# APIGetScanByID get scan from id
# return {'status': '-1'} if something wrong
# return service object if it's success
#

class APIGetScanByID(APIView):
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


######################################################
# APIAddScan add new Scantask
# return {'status': '-1'} if something wrong
# return Vuln object if it's success
#

class APIAddScan(APIView):

    def post(self, request, format=None):
        scanAddForm = ScanAddForm(request.POST)
        if scanAddForm.is_valid():
            scanObj = scanAddForm.save(commit=False)
            scanObj.scanBy = User.objects.get(pk=1)
            scanObj.submitter = User.objects.get(pk=1)
            # scanObj.fileAttachment = request.FILES['fileAttachment']
            scanObj.save()
            dataSerialized = ScanSerializer(scanObj, many=False)
            return Response({'status': '0', 'object': dataSerialized.data})
        else:
            return Response({'status': '-1', 'message': 'Form is invalid', 'detail': scanAddForm.errors})


######################################################
# APIDeleteScan delete existing Scan Tasks
# return {'retVal': '-1'} if id not found
# return {'retVal': 'Num of Success on Deleting'} if it's success
#

class APIDeleteScan(APIView):
    def post(self, request):
        scanForm = ScanIDForm(request.POST)
        if scanForm.is_valid():
            successOnDelete = 0
            try:
                ids = scanForm.data['id'].split(',')
                idLength = len(ids)
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
                        retVuln = ScanTaskModel.objects.get(pk=id)
                    except ScanTaskModel.DoesNotExist:
                        pass
                    else:
                        retVuln.delete()
                        successOnDelete = successOnDelete + 1
            if successOnDelete==1:
                return Response(
                    {'status': '0', 'message': '1 Scanning Task is successfully deleted.', 'numDeleted':successOnDelete})
            else:
                return Response(
                {'status': '0', 'message': '{} Scanning Tasks are successfully deleted.'.format(successOnDelete), 'numDeleted': successOnDelete})
        else:
            return Response({'status': '-1', 'message': 'Form is invalid', 'detail': {scanForm.errors}})


######################################################
# APIUpdateScan update Scan Tasks
# return {'notification': 'error_msg'} if id not found
# return Scan object if it's success
#

class APIUpdateScan(APIView):
    def post(self, request):
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


######################################################
# Get attachment of Scan Task
# return {'notification': 'error_msg'} if id not found
# return Scan object if it's success
#
class APIGetScanAttachment(APIView):
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
            dataSerialized = ScanAttachmentSerializer(retService, many=False)
            return Response(dataSerialized.data)
        else:
            return Response({'status': '-1', 'message': 'fields are required',
                             'detail': {"id": [{"message": "ID is required", "code": "required"}]}})


######################################################
# Add attachment update Scan Tasks
# return {'notification': 'error_msg'} if id not found
# return Scan object if it's success
#
class APIAddAttachment(APIView):
    parser_classes = (MultiPartParser, FormParser, FileUploadParser,)

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


######################################################
# Delete attachment update Scan Tasks
# return {'notification': 'error_msg'} if id not found
# return Scan object if it's success
#

class APIDeleteAttachment(APIView):

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

