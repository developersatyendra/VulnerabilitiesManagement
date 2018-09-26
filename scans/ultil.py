from rest_framework.response import Response
from django.db.models import Q, Count
from .models import ScanTaskModel
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

def GetScansVuln(*args, **kwargs):
    scanTask = ScanTaskModel.objects.all()

    ######################################################
    # Adv Filter
    #
    # Filter by project
    if 'projectID' in kwargs:
        try:
            projectID = int(kwargs.get('projectID'))
        except ValueError:
            return {'status': -1, 'message': "projectID is not integer"}
        scanTask = scanTask.filter(scanProject=projectID)

    # Filter by host
    if 'hostID' in kwargs:
        try:
            hostID = int(kwargs.get('hostID'))
        except ValueError:
            return {'status': -1, 'message': "hostID is not integer"}
        scanTask = scanTask.filter(ScanInfoScanTask__hostScanned__id=hostID)

    # Filter by vuln
    if 'vulnID' in kwargs:
        try:
            vulnID = int(kwargs.get('vulnID'))
        except ValueError:
            return {'status': -1, 'message': "vulnID is not integer"}
        scanTask = scanTask.filter(ScanInfoScanTask__vulnFound__id=vulnID)

    scanTask =  scanTask.annotate(
            # high=Count('ScanInfoScanTask__vulnFound', filter=Q(ScanInfoScanTask__vulnFound__levelRisk__gte=LEVEL_HIGH), distinct=True),
            # med=Count('ScanInfoScanTask__vulnFound', filter=(Q(ScanInfoScanTask__vulnFound__levelRisk__gte=LEVEL_MED) & Q(ScanInfoScanTask__vulnFound__levelRisk__lt=LEVEL_HIGH)), distinct=True),
            # low=Count('ScanInfoScanTask__vulnFound', filter=Q(ScanInfoScanTask__vulnFound__levelRisk__gt=LEVEL_INFO) & Q(ScanInfoScanTask__vulnFound__levelRisk__lt=LEVEL_MED), distinct=True),
            # info=Count('ScanInfoScanTask__vulnFound', filter=Q(ScanInfoScanTask__vulnFound__levelRisk=LEVEL_INFO), distinct=True),
            # numHost=Count('ScanInfoScanTask', distinct=True))
        high = Count('ScanInfoScanTask__vulnFound', filter=Q(ScanInfoScanTask__vulnFound__levelRisk__gte=LEVEL_HIGH)),
        med = Count('ScanInfoScanTask__vulnFound', filter=(Q(ScanInfoScanTask__vulnFound__levelRisk__gte=LEVEL_MED) & Q(
            ScanInfoScanTask__vulnFound__levelRisk__lt=LEVEL_HIGH))),
        low = Count('ScanInfoScanTask__vulnFound', filter=Q(ScanInfoScanTask__vulnFound__levelRisk__gt=LEVEL_INFO) & Q(
            ScanInfoScanTask__vulnFound__levelRisk__lt=LEVEL_MED)),
        info = Count('ScanInfoScanTask__vulnFound', filter=Q(ScanInfoScanTask__vulnFound__levelRisk=LEVEL_INFO)),
        numHost = Count('ScanInfoScanTask', distinct=True))

    ######################################################
    # Filter by day range
    #
    if 'dayRange' in kwargs:
        try:
            dayRange = int(kwargs.get('dayRange'))
        except ValueError:
            return {'status': -1, 'message': "dayRange is not integer"}
        filterDate = (datetime.now() - timedelta(days=dayRange)).date()
        scanTask = scanTask.filter(startTime__gte=filterDate)
    ######################################################
    # Filter by search keyword
    #
    if 'searchText' in kwargs:
        search = kwargs.get('searchText')
        query = Q(name__icontains=search) | \
                Q(startTime__icontains=search) | \
                Q(endTime__icontains=search)
        scanTask = scanTask.filter(query)

    # Set filter to get distinct entry only
    scanTask = scanTask.distinct()

    # Get number of object
    numObject = scanTask.count()

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
        sortString = ['-high', '-med', '-low', '-info', 'name']

    scanTask = scanTask.order_by(*sortString)

    # # Get Page Number
    # if request.GET.get('pageNumber'):
    #     try:
    #         page = int(request.GET.get('pageNumber'))
    #     except ValueError:
    #         page = PAGE_DEFAULT
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
    # querySetPaged = Paginator(scanTask, int(numEntry))
    # dataPaged = querySetPaged.get_page(page)
    # dataSerialized = ScanVulnSerializer(dataPaged, many=True)
    # data = dict()
    # data["total"] = numObject
    # data['rows'] = dataSerialized.data
    return {'status': 0, 'object': scanTask}