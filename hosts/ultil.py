from .models import HostModel
from scans.models import ScanInfoModel
from .serializers import HostSerializer, HostVulnSerializer
from django.core.paginator import Paginator
from django.db.models import Q, Count, F, Max
from rest_framework.response import Response
from django.conf import settings

PAGE_DEFAULT = 1
NUM_ENTRY_DEFAULT = 50

LEVEL_HIGH = getattr(settings, 'LEVEL_HIGH')

# Med is >= LEVEL_MED AND < LEVEL_HIGH
LEVEL_MED = getattr(settings, 'LEVEL_MED')

# Low is > LEVEL_INFO AND < LEVEL_MED
# Info is = LEVEL_INFO
LEVEL_INFO = getattr(settings, 'LEVEL_INFO')


def GetHosts(*args, **kwargs):
    hostQuery = Q()

    # Project Filter
    projectID = kwargs.get('projectID', None)
    if projectID:
        try:
            projectID = int(projectID)
        except (ValueError, TypeError) as e:
            return {'status': -1, 'message': str(e)}
        hostQuery = Q(ScanInfoHost__scanTask__scanProject=projectID)

    # Scan Filter
    scanID = kwargs.get('scanID', None)
    if scanID:
        try:
            scanID = int(scanID)
        except (ValueError, TypeError) as e:
            return {'status': -1, 'message': str(e)}
        hostQuery = hostQuery & Q(ScanInfoHost__scanTask=scanID)

    # Host Filter
    hostID = kwargs.get('hostID', None)
    if hostID:
        try:
            hostID = int(hostID)
        except (ValueError, TypeError) as e:
            return {'status': -1, 'message': str(e)}
        hostQuery = hostQuery & Q(id=hostID)

    # Vuln Filter
    vulnID = kwargs.get('vulnID', None)
    if vulnID:
        try:
            vulnID = int(vulnID)
        except (ValueError, TypeError) as e:
            return {'status': -1, 'message': str(e)}
        hostQuery = hostQuery & Q(ScanInfoHost__vulnFound=vulnID)

    # Serivce Filter
    serviceID = kwargs.get('serviceID', None)
    if serviceID:
        try:
            serviceID = int(serviceID)
        except (ValueError, TypeError) as e:
            return {'status': -1, 'message': str(e)}
        hostQuery = hostQuery & Q(services=serviceID)

    hosts = HostModel.objects.filter(hostQuery).distinct()

    # Check if need for serialize
    serializer = kwargs.get('serializer', None)
    if serializer:
        serializedData = serializer(hosts, many=True)
        return {'status': 0, 'object': serializedData.data}
    return {'status': 0, 'object': hosts}


# APIGetHostsVuln get host with vuln from these params:
def GetHostsVuln(*args, **kwargs):
    retval = GetHosts(**kwargs)
    if retval['status'] != 0:
        return {'status': retval['status'], 'message': retval['message']}

    hostQuery = retval['object'].distinct()
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
    return {'status': 0, 'object': querySet, 'total': numObject}


def GetHostsCurrentVuln(*args, **kwargs):
    retval = GetHosts(**kwargs)
    if retval['status'] != 0:
        return {'status': retval['status'], 'message': retval['message']}
    hostQuery = retval['object']

    hostQuery = hostQuery.distinct()
    scanInfoIDs = hostQuery.annotate(currentDate=Max('ScanInfoHost__scanTask__startTime')).filter(ScanInfoHost__scanTask__startTime=F('currentDate')).values_list('id', flat=True)
    querySet = ScanInfoModel.objects.filter(id__in=scanInfoIDs).values('hostScanned').annotate(
        high=Count('vulnFound', filter=Q(vulnFound__levelRisk__gte=LEVEL_HIGH), distinct=True),
        med=Count('vulnFound', filter=(Q(vulnFound__levelRisk__gte=LEVEL_MED)&Q(vulnFound__levelRisk__lt=LEVEL_HIGH)),distinct=True),
        low=Count('vulnFound', filter=Q(vulnFound__levelRisk__gt=LEVEL_INFO)&Q(vulnFound__levelRisk__lt=LEVEL_MED), distinct=True),
        info=Count('vulnFound', filter=Q(vulnFound__levelRisk=LEVEL_INFO), distinct=True),
        idScan=F('scanTask__id'),
        scanName=F('scanTask__name'),
        startTime=F('scanTask__startTime'),
        hostName=F('hostScanned__hostName'),
        ipAddr=F('hostScanned__ipAddr'),
        id=F('hostScanned__id')
    ).values(
        'id',
        'ipAddr',
        'hostName',
        'high',
        'med',
        'low',
        'info',
        'idScan',
        'scanName',
        'startTime'
    )

    # Filter by search
    if 'searchText' in kwargs:
        search = kwargs.get('searchText')
        query = Q(ipAddr__icontains=search)\
                | Q(hostName__icontains=search)\
                | Q(high__icontains=search) \
                | Q(med__icontains=search) \
                | Q(low__icontains=search) \
                | Q(scanName__icontains=search)

        querySet = querySet.filter(query)
    numObject = querySet.count()

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
    querySet = querySet.order_by(*sortString)
    return {'status': 0, 'object': querySet, 'total': numObject}
