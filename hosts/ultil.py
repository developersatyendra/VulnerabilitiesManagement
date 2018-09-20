from .models import HostModel
from .serializers import HostSerializer, HostVulnSerializer
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

def GetHostsVuln(*args, **kwargs):
    hostQuery = HostModel.objects.all()

    ######################################################
    # Adv Filter

    # Filter by serviceID
    if 'serviceID' in kwargs:
        try:
            serviceID = int(kwargs.get('serviceID'))
        except ValueError:
            return{'status': -1, 'message': "serviceID is not integer"}
        hostQuery = hostQuery.filter(services=serviceID)

    # Filter by vulnID
    if 'vulnID' in kwargs:
        try:
            vulnID = int(kwargs.get('vulnID'))
        except ValueError:
            return{'status': -1, 'message': "vulnID is not integer"}
        hostQuery = hostQuery.filter(ScanInfoHost__vulnFound=vulnID)

    # Filter by scanTask
    if 'scanID' in kwargs:
        try:
            scanID = int(kwargs.get('scanID'))
        except ValueError:
            return{'status': -1, 'message': "scanID is not integer"}
        hostQuery = hostQuery.filter(ScanInfoHost__scanTask__id=scanID)

    # Filter by project
    if 'projectID' in kwargs:
        try:
            projectID = int(kwargs.get('projectID'))
        except ValueError:
            return{'status': -1, 'message': "projectID is not integer"}
        hostQuery = hostQuery.filter(ScanInfoHost__scanTask__scanProject__id=projectID)

    hostQuery = hostQuery.distinct()
    hostQuery = hostQuery.annotate(
            high=Count('ScanInfoHost__vulnFound', filter=Q(ScanInfoHost__vulnFound__levelRisk__gte=LEVEL_HIGH), distinct=True),
            med=Count('ScanInfoHost__vulnFound', filter=(Q(ScanInfoHost__vulnFound__levelRisk__gte=LEVEL_MED)&Q(ScanInfoHost__vulnFound__levelRisk__lt=LEVEL_HIGH)),distinct=True),
            low=Count('ScanInfoHost__vulnFound', filter=Q(ScanInfoHost__vulnFound__levelRisk__gt=LEVEL_INFO)&Q(ScanInfoHost__vulnFound__levelRisk__lt=LEVEL_MED), distinct=True),
            info=Count('ScanInfoHost__vulnFound', filter=Q(ScanInfoHost__vulnFound__levelRisk=LEVEL_INFO), distinct=True),
            idScan=F('ScanInfoHost__scanTask__id'),
            scanName=F('ScanInfoHost__scanTask__name'),
            startTime=F('ScanInfoHost__scanTask__startTime'))

    # Filter by search keyword
    if 'searchText' in kwargs:
        search = kwargs.get('searchText')
        query = Q(ipAddr__icontains=search)\
                | Q(hostName__icontains=search)\
                | Q(high__icontains=search) \
                | Q(med__icontains=search) \
                | Q(low__icontains=search) \
                | Q(scanName__icontains=search)

        hostQuery = hostQuery.filter(query)
    # get total
    numObject = hostQuery.count()
    # Get sort order
    if 'sortOrder' in kwargs:
        if kwargs.get('sortOrder') == 'asc':
            sortString = ''
        else:
            sortString = '-'
    else:
        sortString = '-'


    # Get sort filed
    if 'sortName' in kwargs:
        sortString = sortString + kwargs.get('sortName')
        sortString = sortString.replace('.', '__')
        sortString = [sortString]
    else:
        sortString = ['-high', '-med', '-low', '-info', 'hostName']
    querySet = hostQuery.order_by(*sortString)

    # # Get Page Number
    # if request.GET.get('pageNumber'):
    #     page = request.GET.get('pageNumber')
    # else:
    #     page = PAGE_DEFAULT
    #
    # # Get Page Size
    # if request.GET.get('pageSize'):
    #     numEntry = request.GET.get('pageSize')
    #     # IF Page size is 'ALL'
    #     if numEntry.lower() == 'all' or numEntry == -1:
    #         numEntry = numObject
    # else:
    #     numEntry = NUM_ENTRY_DEFAULT
    # querySetPaged = Paginator(querySet, int(numEntry))
    # dataPaged = querySetPaged.get_page(page)
    # dataSerialized = HostVulnSerializer(dataPaged, many=True)
    # data = dict()
    # data["total"] = numObject
    # data['rows'] = dataSerialized.data
    return {'status': 0, 'object':querySet}