from rest_framework.response import Response
from django.db.models import Q, Count
from .models import ScanTaskModel
from datetime import datetime, timedelta
import dateutil.parser
from django.conf import settings

PAGE_DEFAULT = 1
NUM_ENTRY_DEFAULT = 50

LEVEL_HIGH = getattr(settings, 'LEVEL_HIGH')

# Med is >= LEVEL_MED AND < LEVEL_HIGH
LEVEL_MED = getattr(settings, 'LEVEL_MED')

# Low is > LEVEL_INFO AND < LEVEL_MED
# Info is = LEVEL_INFO
LEVEL_INFO = getattr(settings, 'LEVEL_INFO')


def GetScans(*args, **kwargs):
    scanQuery = Q()

    # Project Filter
    projectID = kwargs.get('projectID', None)
    if projectID:
        try:
            projectID = int(projectID)
        except (ValueError, TypeError) as e:
            return {'status': -1, 'message': str(e)}
        scanQuery = Q(scanProject=projectID)

    # Scan Filter
    scanID = kwargs.get('scanID', None)
    if scanID:
        try:
            scanID = int(scanID)
        except (ValueError, TypeError) as e:
            return {'status': -1, 'message': str(e)}
        scanQuery = scanQuery & Q(id=scanID)

    # Host Filter
    hostID = kwargs.get('hostID', None)
    if hostID:
        try:
            hostID = int(hostID)
        except (ValueError, TypeError) as e:
            return {'status': -1, 'message': str(e)}
        scanQuery = scanQuery & Q(ScanInfoScanTask__hostScanned=hostID)

    # Vuln Filter
    vulnID = kwargs.get('vulnID', None)
    if vulnID:
        try:
            vulnID = int(vulnID)
        except (ValueError, TypeError) as e:
            return {'status': -1, 'message': str(e)}
        scanQuery = scanQuery & Q(ScanInfoScanTask__vulnFound=vulnID)

    # Serivce Filter
    serviceID = kwargs.get('serviceID', None)
    if serviceID:
        try:
            serviceID = int(serviceID)
        except (ValueError, TypeError) as e:
            return {'status': -1, 'message': str(e)}
        tempQuery = Q(ScanInfoScanTask__vulnFound__service=serviceID) | Q(ScanInfoScanTask__hostScanned__services=serviceID)
        scanQuery = scanQuery & tempQuery

    # SearchText Filter
    searchText = kwargs.get('searchText', None)
    if searchText:
        tempQuery = Q(name__icontains=searchText) | \
                    Q(description__icontains=searchText)
        scanQuery = scanQuery & tempQuery

    # FromDate Filter
    fromDate = kwargs.get('fromDate', None)
    if fromDate:
        try:
            fromDate = dateutil.parser.parse(fromDate)
        except (ValueError, TypeError) as e:
            return {'status': -1, 'message': str(e)}
        scanQuery = scanQuery & Q(startTime__gte=fromDate)

    toDate = kwargs.get('toDate', None)
    if toDate:
        try:
            toDate = dateutil.parser.parse(toDate)
        except (ValueError, TypeError) as e:
            return {'status': -1, 'message': str(e)}
        scanQuery = scanQuery & Q(startTime__lte=toDate)

    # Get objects
    scans = ScanTaskModel.objects.filter(scanQuery).distinct()

    # Check if need for serialize
    serializer = kwargs.get('serializer', None)
    if serializer:
        serializedData = serializer(scans, many=True)
        return {'status': 0, 'object': serializedData.data}
    return {'status': 0, 'object': scans}


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
    retval = GetScans(**kwargs)
    if retval['status'] != 0:
        return {'status': retval['status'], 'message': retval['message']}
    scanTask = retval['object'].distinct()

    scanTask = scanTask.annotate(
        high = Count('ScanInfoScanTask__vulnFound', filter=Q(ScanInfoScanTask__vulnFound__levelRisk__gte=LEVEL_HIGH)),
        med = Count('ScanInfoScanTask__vulnFound', filter=(Q(ScanInfoScanTask__vulnFound__levelRisk__gte=LEVEL_MED) & Q(
            ScanInfoScanTask__vulnFound__levelRisk__lt=LEVEL_HIGH))),
        low = Count('ScanInfoScanTask__vulnFound', filter=Q(ScanInfoScanTask__vulnFound__levelRisk__gt=LEVEL_INFO) & Q(
            ScanInfoScanTask__vulnFound__levelRisk__lt=LEVEL_MED)),
        info = Count('ScanInfoScanTask__vulnFound', filter=Q(ScanInfoScanTask__vulnFound__levelRisk=LEVEL_INFO)),
        numHost = Count('ScanInfoScanTask', distinct=True))

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
    return {'status': 0, 'object': scanTask, 'total':numObject}