from django.db.models import Q, Count, Max, F
from .models import ServiceModel
from hosts.ultil import GetHosts
from scans.models import ScanInfoModel
from django.conf import settings

PAGE_DEFAULT = 1
NUM_ENTRY_DEFAULT = 50

LEVEL_HIGH = getattr(settings, 'LEVEL_HIGH')

# Med is >= LEVEL_MED AND < LEVEL_HIGH
LEVEL_MED = getattr(settings, 'LEVEL_MED')

# Low is > LEVEL_INFO AND < LEVEL_MED
# Info is = LEVEL_INFO
LEVEL_INFO = getattr(settings, 'LEVEL_INFO')


def GetServices(*args, **kwargs):
    serviceQuery = Q()

    # Project Filter
    projectID = kwargs.get('projectID', None)
    if projectID:
        try:
            projectID = int(projectID)
        except (ValueError, TypeError) as e:
            return {'status': -1, 'message': str(e)}
        serviceQuery = Q(ServiceVulnerability__ScanInfoVuln__scanTask__scanProject=projectID)

    # Scan Filter
    scanID = kwargs.get('scanID', None)
    if scanID:
        try:
            scanID = int(scanID)
        except (ValueError, TypeError) as e:
            return {'status': -1, 'message': str(e)}
        serviceQuery = serviceQuery & Q(ServiceVulnerability__ScanInfoVuln__scanTask=scanID)

    # Host Filter
    hostID = kwargs.get('hostID', None)
    if hostID:
        try:
            hostID = int(hostID)
        except (ValueError, TypeError) as e:
            return {'status': -1, 'message': str(e)}
        serviceQuery = serviceQuery & Q(ServiceHost=hostID)

    # Vuln Filter
    vulnID = kwargs.get('vulnID', None)
    if vulnID:
        try:
            vulnID = int(vulnID)
        except (ValueError, TypeError) as e:
            return {'status': -1, 'message': str(e)}
        serviceQuery = serviceQuery & Q(ServiceVulnerability=vulnID)

    # Serivce Filter
    serviceID = kwargs.get('serviceID', None)
    if serviceID:
        try:
            serviceID = int(serviceID)
        except (ValueError, TypeError) as e:
            return {'status': -1, 'message': str(e)}
        serviceQuery = serviceQuery & Q(id=serviceID)

    services = ServiceModel.objects.filter(serviceQuery)

    # Check if need for serialize
    serializer = kwargs.get('serializer', None)
    if serializer:
        serializedData = serializer(services, many=True)
        return {'status': 0, 'object': serializedData.data}
    return {'status': 0, 'object': services}


def GetServicesVuln(*args, **kwargs):
    retval = GetHosts(**kwargs)
    if retval['status'] != 0:
        return {'status': retval['status'], 'message': retval['message']}
    hostQuery = retval['object']

    hostQuery = hostQuery.distinct()
    scanInfoIDs = hostQuery.annotate(currentDate=Max('ScanInfoHost__scanTask__startTime')).filter(
        ScanInfoHost__scanTask__startTime=F('currentDate')).values_list('ScanInfoHost__id', flat=True)

    serviceVuln = ScanInfoModel.objects.filter(id__in=scanInfoIDs).values('vulnFound__service').annotate(
        high=Count('vulnFound', filter=Q(vulnFound__levelRisk__gte=LEVEL_HIGH), distinct=True),
        med=Count('vulnFound', filter=(Q(vulnFound__levelRisk__gte=LEVEL_MED) & Q(vulnFound__levelRisk__lt=LEVEL_HIGH)), distinct=True),
        low=Count('vulnFound', filter=Q(vulnFound__levelRisk__gt=LEVEL_INFO) & Q(vulnFound__levelRisk__lt=LEVEL_MED), distinct=True),
        info=Count('vulnFound', filter=Q(vulnFound__levelRisk=LEVEL_INFO), distinct=True),
        total=Count('vulnFound', distinct=True),
        id=F('vulnFound__service'),
        name=F('vulnFound__service__name'),
        port=F('vulnFound__service__port'),
    ).values(
        'id', 'name', 'port', 'high', 'med', 'low', 'total', 'info'
    )

    # searchText
    search = kwargs.get('searchText', None)
    if search:
        query = Q(name__icontains=search)
        serviceVuln = serviceVuln.filter(query)

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
        sortString = ['-high', '-med', '-low', '-info', 'name', 'port']
    serviceVuln = serviceVuln.order_by(*sortString)
    return {'status':0, 'object': serviceVuln}