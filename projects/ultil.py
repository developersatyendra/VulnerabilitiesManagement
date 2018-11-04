from django.db.models import Q, F, Max, Sum
from .serializers import *
from hosts.ultil import GetHostsCurrentVuln
from scans.models import ScanTaskModel
import dateutil.parser
from django.conf import settings
from operator import itemgetter

PAGE_DEFAULT = 1
NUM_ENTRY_DEFAULT = 50

LEVEL_HIGH = getattr(settings, 'LEVEL_HIGH')

# Med is >= LEVEL_MED AND < LEVEL_HIGH
LEVEL_MED = getattr(settings, 'LEVEL_MED')

# Low is > LEVEL_INFO AND < LEVEL_MED
# Info is = LEVEL_INFO
LEVEL_INFO = getattr(settings, 'LEVEL_INFO')


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


# GetProjectVuln get project with vuln from these params:
def GetProjectVuln(*args, **kwargs):
    retval = GetProject(**kwargs)
    if retval['status'] != 0:
        return {'status': retval['status'], 'message': retval['message']}
    projectQuery = retval['object'].distinct()

    projectVul = []
    for project in projectQuery:
        retval = GetHostsCurrentVuln(projectID=project.id)
        if retval['status'] != 0:
            return retval
        totalVuln = retval['object'].aggregate(High=Sum('high'), Med=Sum('med'), Low=Sum('low'), Info=Sum('info'))
        numScanTasks = ScanTaskModel.objects.filter(scanProject=project).count()
        projectVul.append({
            'id': project.id,
            'name': project.name,
            'numScanTasks':numScanTasks,
            'high': totalVuln['High'] if totalVuln['High'] else 0,
            'med': totalVuln['Med'] if totalVuln['Med'] else 0,
            'low': totalVuln['Low'] if totalVuln['Low'] else 0,
            'info': totalVuln['Info'] if totalVuln['Info'] else 0
        })
    sortName = kwargs.get('sortName', None)
    if sortName and sortName in ['id', 'name', 'high', 'med', 'low', 'info']:
        sortOrder = kwargs.get('sortOrder', None)
        if sortOrder =='asc':
            reverse = False
        else:
            reverse = True
        projectVul = sorted(projectVul, key=itemgetter(sortName), reverse=reverse)
    else:
        projectVul = sorted(projectVul, key=itemgetter('high', 'med', 'low', 'info'), reverse=True)
    return {'status': 0, 'object': projectVul}
