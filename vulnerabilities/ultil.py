from django.core.paginator import Paginator
from django.db.models import Q
from .models import VulnerabilityModel
from django.db.models import Count, Case, When, IntegerField
import operator
from functools import reduce
from scans.models import ScanTaskModel


PAGE_DEFAULT = 1
NUM_ENTRY_DEFAULT = 50
LINUX_OS = ['ubuntu', 'kali', 'fedora', 'redhat', 'rhel', 'oracle', 'gento', 'mint', 'linux']
UNIX_OS = ['aix', 'unix']

######################################################
# GetVulns get vulns from these params:
#   searchText: Search content
#   sortName: Name of column is applied sort
#   sortOrder: sort entry by order 'asc' or 'desc'
#   pageSize: number of entry per page
#   pageNumber: page number of curent view
#   projectID: project to be used to filter
#   scanID: ScanTask to be used to filter
#   hostID: Vuln to be used to filter
#   serviceID: Service to be used to filter

def GetVulns(*args, **kwargs):

    # Filter by search keyword
    if 'searchText' in kwargs:
        search = kwargs.get('searchText')
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
    if 'serviceID' in kwargs:
        try:
            serviceID = int(kwargs.get('serviceID'))
        except ValueError:
            return {'status': -1, 'message': "serviceID is not integer"}
        querySet = querySet.filter(service=serviceID)

    # Filter by project
    if 'projectID' in kwargs:
        try:
            projectID = int(kwargs.get('projectID'))
        except ValueError:
            return {'status': -1, 'message': "projectID is not integer"}
        querySet = querySet.filter(ScanInfoVuln__scanTask__scanProject=projectID)

    # Filter by scanTask
    if 'scanID' in kwargs:
        try:
            scanID = int(kwargs.get('scanID'))
        except ValueError:
            return {'status': -1, 'message': "scanID is not integer"}
        querySet = querySet.filter(ScanInfoVuln__scanTask__id=scanID)

    # Filter by host
    if 'hostID' in kwargs:
        try:
            hostID = int(kwargs.get('hostID'))
        except ValueError:
            return {'status': -1, 'message': "hostID is not integer"}
        querySet = querySet.filter(ScanInfoVuln__hostScanned__id=hostID)

    querySet=querySet.distinct()

    # get total
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
    else:
        sortString = sortString + 'levelRisk'
    sortString = sortString.replace('.', '__')
    querySet = querySet.order_by(sortString)
    # Get Page Number
    if 'pageNumber' in kwargs:
        try:
            page = int(kwargs.get('pageNumber'))
        except ValueError:
            return {'status': -1, 'message': "pageNumber is not integer"}
    else:
        page = PAGE_DEFAULT

    # Get Page Size
    if 'pageSize' in kwargs:
        numEntry = kwargs.get('pageSize')

        # IF Page size is 'ALL'
        if numEntry.lower() == 'all' or numEntry == -1:
            numEntry = numObject
        else:
            try:
                numEntry = int(kwargs.get('pageSize'))
            except ValueError:
                return {'status': -1, 'message': "pageSize is not integer"}
    else:
        numEntry = NUM_ENTRY_DEFAULT
    querySetPaged = Paginator(querySet, int(numEntry))
    dataPaged = querySetPaged.get_page(page)
    return {'status':0, 'object': querySet}


def VulnStatisticByOS(*args, **kwargs):
    vulns = GetVulns(*args, **kwargs)
    if vulns['status'] != 0:
        return -1
    vulnQuerySet = vulns['object']

    # Filter Linux
    queryLinux = reduce(operator.or_, (Q(ScanInfoVuln__hostScanned__osName__icontains = item) for item in LINUX_OS))

    # Filter UNIX
    queryUnix = reduce(operator.or_, (Q(ScanInfoVuln__hostScanned__osName__icontains=item) for item in UNIX_OS))

    # Filter Windows
    queryWindows = Q(ScanInfoVuln__hostScanned__osName__icontains='windows')

    # Filter IOS
    queryIOS = Q(ScanInfoVuln__hostScanned__osName__icontains='ios')


    retVal = vulnQuerySet.aggregate(
        windows=Count(Case(
            When(queryWindows, then=1),
            output_field=IntegerField,
        )),
        ios=Count(Case(
            When(queryIOS, then=1),
            output_field=IntegerField,
        )),
        linux=Count(Case(
            When(queryLinux, then=1),
            output_field=IntegerField,
        )),
        unix=Count(Case(
            When(queryUnix, then=1),
            output_field=IntegerField,
        )),
        other=Count(Case(
            When(~(queryWindows | queryIOS | queryLinux | queryUnix), then=1),
            output_field=IntegerField,
        ))
    )
    return retVal


def VulnStatisticByService(*args, **kwargs):
    vulns = GetVulns(*args, **kwargs)
    if vulns['status'] != 0:
        return -1
    vulnQuerySet = vulns['object']

    # Filter Linux
    services = vulnQuerySet.values_list('service__name')

    result = {}
    for service in services:
        queryService = Q(service__name = service[0])

        numCount = vulnQuerySet.filter(queryService).count()
        result.update({service[0]: numCount})
    return result


def GetCurrentHostVuln(*args,**kwargs):
    if 'hostID' in kwargs:
        hostID = kwargs.get('hostID')
        latestScanTask = ScanTaskModel.objects.filter(ScanInfoScanTask__hostScanned__id=hostID).order_by('-startTime')[0]
        currentVulns = GetVulns(hostID=hostID, scanID=latestScanTask.id)['object']
        return {'status': 0, 'object': currentVulns}
    else:
        return {'status': -1, 'message': "HostID is required"}