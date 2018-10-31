from django.db.models import Q, F, Max
from .serializers import *
from hosts.ultil import GetHosts
import dateutil.parser


def GetProject(*args, **kwargs):
    projectQuery = Q()

    # Project Filter
    projectID = kwargs.get('projectID', None)
    if projectID:
        try:
            projectID = int(projectID)
        except (ValueError, TypeError) as e:
            return {'status': -1, 'message': str(e)}
        projectQuery = projectQuery & Q(id=projectID)

    # Scan Filter
    scanID = kwargs.get('scanID', None)
    if scanID:
        try:
            scanID = int(scanID)
        except (ValueError, TypeError) as e:
            return {'status': -1, 'message': str(e)}
        projectQuery = projectQuery & Q(ScanProjectScanTask=scanID)

    # Host Filter
    hostID = kwargs.get('hostID', None)
    if hostID:
        try:
            hostID = int(hostID)
        except (ValueError, TypeError) as e:
            return {'status': -1, 'message': str(e)}
        projectQuery = projectQuery & Q(ScanProjectScanTask__ScanInfoScanTask__hostScanned=hostID)

    # Vuln Filter
    vulnID = kwargs.get('vulnID', None)
    if hostID:
        try:
            vulnID = int(vulnID)
        except (ValueError, TypeError) as e:
            return {'status': -1, 'message': str(e)}
        projectQuery = projectQuery & Q(ScanProjectScanTask__ScanInfoScanTask__vulnFound=vulnID)

    # Service Filter
    serviceID = kwargs.get('serviceID', None)
    if serviceID:
        try:
            serviceID = int(serviceID)
        except (ValueError, TypeError) as e:
            return {'status': -1, 'message': str(e)}
        tempQuery = Q(ScanProjectScanTask__ScanInfoScanTask__vulnFound__service=serviceID) | Q(ScanProjectScanTask__ScanInfoScanTask__hostScanned__services=serviceID)
        projectQuery = projectQuery & tempQuery

    searchText = kwargs.get('searchText', None)
    if searchText:
        tempQuery = Q(name__icontains=searchText) | \
                Q(description__icontains=searchText)
        projectQuery = projectQuery & tempQuery

    fromDate = kwargs.get('fromDate', None)
    if fromDate:
        try:
            fromDate = dateutil.parser.parse(fromDate)
        except (ValueError, TypeError) as e:
            return {'status': -1, 'message': str(e)}
        projectQuery = projectQuery & Q(ScanProjectScanTask__startTime__gte=fromDate)

    toDate = kwargs.get('toDate', None)
    if toDate:
        try:
            toDate = dateutil.parser.parse(toDate)
        except (ValueError, TypeError) as e:
            return {'status': -1, 'message': str(e)}
        projectQuery = projectQuery & Q(ScanProjectScanTask__startTime__lte=toDate)
    querySet = ScanProjectModel.objects.filter(projectQuery).distinct()

    # Check if need for serialize
    serializer = kwargs.get('serializer', None)
    if serializer:
        serializedData = serializer(querySet, many=True)
        return {'status': 0, 'object': serializedData.data}
    return {'status': 0, 'object': querySet}


# APIGetHostsVuln get host with vuln from these params:

def GetProjectVuln(*args, **kwargs):
    retvul = GetProject(**kwargs)
    if retvul['status'] != 0:
        return {'status': retvul['status'], 'message': retvul['message']}
    projectQuery = retvul['object'].distinct()

    for project in projectQuery:
        hosts = GetHosts(projectID=project.id)
        scanInfoIDs = hosts.annotate(currentDate=Max('ScanInfoHost__scanTask__startTime')).filter(ScanInfoHost__scanTask__startTime=F('currentDate')).values_list('id', flat=True)
        project.filter(ScanProjectScanTask__ScanInfoScanTask__in=scanInfoIDs)

    hostQuery = projectQuery.values_list('ScanProjectScanTask__ScanInfoScanTask__hostScanned', flat=True)
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
