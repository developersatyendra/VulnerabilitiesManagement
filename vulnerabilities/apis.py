from django.utils.datastructures import MultiValueDictKeyError
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.paginator import Paginator
from django.db.models import Q
from services.models import ServiceModel
from scans.models import ScanTaskModel, ScanInfoModel
from .models import VulnerabilityModel
from .serializers import VulnSerializer
from .forms import VulnForm, VulnIDForm


PAGE_DEFAULT = 1
NUM_ENTRY_DEFAULT = 50


######################################################
#   APIGetVulnName get Name of Vuln from id
#

class APIGetVulnName(APIView):
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
    def get(self, request):

        # Filter by search keyword
        if request.GET.get('searchText'):
            search = request.GET.get('searchText')
            # Filter On Vuln
            queryVulnModel = Q(description__icontains=search) \
                             | Q(name__icontains=search) \
                             | Q(observation__icontains=search) \
                             | Q(recommendation__icontains=search) \
                             | Q(cve__icontains=search) \
                             | Q(levelRisk__icontains=search) \
                             | Q(service__name__icontains=search)
            querySet = VulnerabilityModel.objects.filter(queryVulnModel)
        else:
            querySet = VulnerabilityModel.objects.all()

        ######################################################
        # Adv Filter
        #

        # Filter by serviceID
        if request.GET.get('serviceID'):
            try:
                serviceID = int(request.GET.get('serviceID'))
            except ValueError:
                return Response({'status': -1, 'message': "serviceID is not integer"})
            querySet = querySet.filter(service=serviceID)

        # Filter by project
        if request.GET.get('projectID'):
            try:
                projectID = int(request.GET.get('projectID'))
            except ValueError:
                return Response({'status': -1, 'message': "projectID is not integer"})
            querySet = querySet.filter(ScanInfoVuln__scanTask__scanProject=projectID)

        # Filter by scanTask
        if request.GET.get('scanID'):
            try:
                scanID = int(request.GET.get('scanID'))
            except ValueError:
                return Response({'status': -1, 'message': "scanID is not integer"})
            querySet = querySet.filter(ScanInfoVuln__scanTask__id=scanID)

        # Filter by host
        if request.GET.get('hostID'):
            try:
                hostID = int(request.GET.get('hostID'))
            except ValueError:
                return Response({'status': -1, 'message': "hostID is not integer"})
            querySet = querySet.filter(ScanInfoVuln__hostScanned__id=hostID)

        querySet=querySet.distinct()

        # get total
        numObject = querySet.count()
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
        dataSerialized = VulnSerializer(dataPaged, many=True)
        data = dict()
        data["total"] = numObject
        data['rows'] = dataSerialized.data
        return Response({'status':0, 'object':data})


#
# APIGetVulnsByID get vulns from id
# return {'retVal': '-1'} if id not found
# return vuln object if it's success
#

class APIGetVulnByID(APIView):
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
    def get(self, request):
        if request.GET.get('id'):
            try:
                id = int(request.GET.get('id'))
            except ValueError:
                return Response({'status': '-1', 'message': 'Value error',
                                 'detail': {"id": [{"message": "ID is not integer", "code": "value error"}]}})
            scanTask = ScanTaskModel.objects.filter(ScanInfoScanTask__hostScanned=id).order_by('-startTime')[0]
            scanInfo = scanTask.ScanInfoScanTask.get(hostScanned=id)
            vulns = scanInfo.vulnFound.all()
            if request.GET.get('searchText'):
                search = request.GET.get('searchText')
                queryVulnModel = Q(description__icontains=search) \
                                 | Q(name__icontains=search) \
                                 | Q(observation__icontains=search) \
                                 | Q(recommendation__icontains=search) \
                                 | Q(cve__icontains=search) \
                                 | Q(levelRisk__icontains=search) \
                                 | Q(service__name__icontains=search)
                vulns = vulns.filter(queryVulnModel)
            vulns = vulns.distinct()

            # get total
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
                sortString = sortString + 'id'
            sortString = sortString.replace('.', '__')
            querySet = vulns.order_by(sortString)
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
            dataSerialized = VulnSerializer(dataPaged, many=True)
            data = dict()
            data["total"] = numObject
            data['rows'] = dataSerialized.data
            return Response({'status': 0, 'object': data})
        else:
            return Response({'status': '-1', 'message': 'fields are required',
                             'detail': {"id": [{"message": "ID is required", "code": "required"}]}})