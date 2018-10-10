from django.utils.datastructures import MultiValueDictKeyError
from scans.models import ScanTaskModel, ScanInfoModel
from .models import HostModel
from .forms import HostForm, HostIDForm
from .serializers import HostSerializer, HostVulnSerializer
from .ultil import GetHostsVuln
from django.contrib.auth.models import User
from rest_framework.views import APIView
from django.core.paginator import Paginator
from django.db.models import Q, Count, F
from rest_framework.response import Response

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
#   APIGetHostName get Name of Host from id
#

class APIGetHostName(APIView):
    def get(self, request):
        if request.GET.get('id'):
            try:
                id = int(request.GET.get('id'))
            except (ValueError, TypeError):
                return Response({'status': '-1', 'message': 'Value error',
                                 'detail': {"id": [{"message": "ID is not integer", "code": "value error"}]}})
            try:
                name = HostModel.objects.get(pk=id).hostName
            except HostModel.DoesNotExist:
                return Response({'status': '-1', 'message': 'Host does not exist'})
            return Response({'status': 0, 'object':name})
        else:
            return Response({'status': '-1', 'message': 'fields are required',
                             'detail': {"id": [{"message": "ID is required", "code": "required"}]}})


# APIGetHostsVuln get host with vuln from these params:
#   searchText: Search content
#   sortName: Name of column is applied sort
#   sortOrder: sort entry by order 'asc' or 'desc'
#   pageSize: number of entry per page
#   pageNumber: page number of curent view
#   projectID: project to be used to filter
#   scanID: ScanTask to be used to filter
#   vulnID: Vuln to be used to filter
#   serviceID: Service to be used to filter

class APIGetHostsVuln(APIView):

    def get(self, request):
        params = dict()
        projectID = request.GET.getlist("projectID", None)
        scanID = request.GET.getlist("scanID", None)
        serviceID = request.GET.getlist("serviceID", None)
        vulnID = request.GET.getlist("vulnID", None)
        searchText = request.GET.get('searchText', None)
        sortOrder = request.GET.get('sortOrder')
        sortName = request.GET.get('sortName')
        
        if projectID:
            params['projectID'] = projectID
        
        if scanID:
            params['scanID'] = scanID
        
        if serviceID:
            params['serviceID'] = serviceID

        if vulnID:
            params['vulnID'] = vulnID
        
        if searchText:
            params['searchText'] = searchText
        
        if sortOrder:
            params['sortOrder'] = sortOrder

        if sortName:
            params['sortName'] = sortName

        retval = GetHostsVuln(**params)

        if retval['status'] == 0:
            if request.GET.get('pageNumber'):
                try:
                    page = int(request.GET.get('pageNumber'))
                except TypeError:
                    page = PAGE_DEFAULT
            else:
                page = PAGE_DEFAULT

            # Get Page Size
            if request.GET.get('pageSize'):
                try:
                    numEntry = int(request.GET.get('pageSize'))
                except TypeError:
                    numEntry = NUM_ENTRY_DEFAULT
                # IF Page size is 'ALL'
                if str(numEntry).lower() == 'all' or numEntry == -1:
                    numEntry = retval['total']
            else:
                numEntry = NUM_ENTRY_DEFAULT
            querySetPaged = Paginator(retval['object'], numEntry)
            dataPaged = querySetPaged.get_page(page)
            dataSerialized = HostVulnSerializer(dataPaged, many=True)
            object = {
                'total': retval['total'],
                'rows': dataSerialized.data
            }
            return Response({'status': 0, 'object': object})
        else:
            return Response(retval)
    # def get(self, request):
    #     hostQuery = HostModel.objects.all()
    #
    #     ######################################################
    #     # Adv Filter
    #
    #     # Filter by serviceID
    #     if request.GET.get('serviceID'):
    #         try:
    #             serviceID = int(request.GET.get('serviceID'))
    #         except ValueError:
    #             return Response({'status': -1, 'message': "serviceID is not integer"})
    #         hostQuery = hostQuery.filter(services=serviceID)
    #
    #     # Filter by vulnID
    #     if request.GET.get('vulnID'):
    #         try:
    #             vulnID = int(request.GET.get('vulnID'))
    #         except ValueError:
    #             return Response({'status': -1, 'message': "vulnID is not integer"})
    #         hostQuery = hostQuery.filter(ScanInfoHost__vulnFound=vulnID)
    #
    #     # Filter by scanTask
    #     if request.GET.get('scanID'):
    #         try:
    #             scanID = int(request.GET.get('scanID'))
    #         except ValueError:
    #             return Response({'status': -1, 'message': "scanID is not integer"})
    #         hostQuery = hostQuery.filter(ScanInfoHost__scanTask__id=scanID)
    #
    #     # Filter by project
    #     if request.GET.get('projectID'):
    #         try:
    #             projectID = int(request.GET.get('projectID'))
    #         except ValueError:
    #             return Response({'status': -1, 'message': "projectID is not integer"})
    #         hostQuery = hostQuery.filter(ScanInfoHost__scanTask__scanProject__id=projectID)
    #
    #     hostQuery = hostQuery.distinct()
    #     hostQuery = hostQuery.annotate(
    #             high=Count('ScanInfoHost__vulnFound', filter=Q(ScanInfoHost__vulnFound__levelRisk__gte=LEVEL_HIGH), distinct=True),
    #             med=Count('ScanInfoHost__vulnFound', filter=(Q(ScanInfoHost__vulnFound__levelRisk__gte=LEVEL_MED)&Q(ScanInfoHost__vulnFound__levelRisk__lt=LEVEL_HIGH)),distinct=True),
    #             low=Count('ScanInfoHost__vulnFound', filter=Q(ScanInfoHost__vulnFound__levelRisk__gt=LEVEL_INFO)&Q(ScanInfoHost__vulnFound__levelRisk__lt=LEVEL_MED), distinct=True),
    #             info=Count('ScanInfoHost__vulnFound', filter=Q(ScanInfoHost__vulnFound__levelRisk=LEVEL_INFO), distinct=True),
    #             idScan=F('ScanInfoHost__scanTask__id'),
    #             scanName=F('ScanInfoHost__scanTask__name'),
    #             startTime=F('ScanInfoHost__scanTask__startTime'))
    #
    #     # Filter by search keyword
    #     if request.GET.get('searchText'):
    #         search = request.GET.get('searchText')
    #         query = Q(ipAddr__icontains=search)\
    #                 | Q(hostName__icontains=search)\
    #                 | Q(high__icontains=search) \
    #                 | Q(med__icontains=search) \
    #                 | Q(low__icontains=search) \
    #                 | Q(scanName__icontains=search)
    #
    #         hostQuery = hostQuery.filter(query)
    #     # get total
    #     numObject = hostQuery.count()
    #     # Get sort order
    #     if request.GET.get('sortOrder') == 'asc':
    #         sortString = ''
    #     else:
    #         sortString = '-'
    #
    #     # Get sort filed
    #     if request.GET.get('sortName'):
    #         sortString = sortString + request.GET.get('sortName')
    #         sortString = sortString.replace('.', '__')
    #         sortString = [sortString]
    #     else:
    #         sortString = ['-high', '-med', '-low', '-info', 'hostName']
    #     querySet = hostQuery.order_by(*sortString)
    #     # Get Page Number
    #     if request.GET.get('pageNumber'):
    #         page = request.GET.get('pageNumber')
    #     else:
    #         page = PAGE_DEFAULT
    #
    #     # Get Page Size
    #     if request.GET.get('pageSize'):
    #         numEntry = request.GET.get('pageSize')
    #         # IF Page size is 'ALL'
    #         if numEntry.lower() == 'all' or numEntry == -1:
    #             numEntry = numObject
    #     else:
    #         numEntry = NUM_ENTRY_DEFAULT
    #     querySetPaged = Paginator(querySet, int(numEntry))
    #     dataPaged = querySetPaged.get_page(page)
    #     dataSerialized = HostVulnSerializer(dataPaged, many=True)
    #     data = dict()
    #     data["total"] = numObject
    #     data['rows'] = dataSerialized.data
    #     return Response({'status': 0, 'object':data})


# APIGetHosts get host from these params:
#   searchText: Search content
#   sortName: Name of column is applied sort
#   sortOrder: sort entry by order 'asc' or 'desc'
#   pageSize: number of entry per page
#   pageNumber: page number of curent view
#   projectID: project to be used to filter
#   scanID: ScanTask to be used to filter
#   vulnID: Vuln to be used to filter
#   serviceID: Service to be used to filter

class APIGetHosts(APIView):
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

        # Filter by scanTask
        if request.GET.get('scanID'):
            try:
                scanID = int(request.GET.get('scanID'))
            except ValueError:
                return Response({'status': -1, 'message': "scanID is not integer"})
            scanTask = scanTask.filter(id=scanID)

        # Get ScanInfo
        scanInfoIDs = scanTask.values_list('ScanInfoScanTask', flat=True).distinct()
        scanInfo = ScanInfoModel.objects.filter(id__in=scanInfoIDs)

        # Filter by vulnID
        if request.GET.get('vulnID'):
            try:
                vulnID = int(request.GET.get('vulnID'))
            except ValueError:
                return Response({'status': -1, 'message': "vulnID is not integer"})
            scanInfo = scanInfo.filter(vulnFound=vulnID)

        hostID = scanInfo.values_list('hostScanned', flat=True)
        host = HostModel.objects.filter(id__in=hostID)
        # Filter by serviceID
        if request.GET.get('serviceID'):
            try:
                serviceID = int(request.GET.get('serviceID'))
            except ValueError:
                return Response({'status': -1, 'message': "serviceID is not integer"})
            host = host.filter(services=serviceID)


        # Filter by search keyword
        if request.GET.get('searchText'):
            search = request.GET.get('searchText')
            query = Q(ipAddr__icontains=search)\
                    | Q(hostName__icontains=search)\
                    | Q(osName__icontains=search) \
                    | Q(osVersion__icontains=search) \
                    | Q(description__icontains=search)
            host = host.filter(query)

        # get total
        numObject = host.count()
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
        querySet = host.order_by(sortString)

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
            entry.createBy = User.objects.get(username=request.user)
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