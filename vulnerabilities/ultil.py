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
        rawSearch = kwargs.get('searchText', None)
        if type(rawSearch) is list:
            queryVulnModel = None
            for search in rawSearch:
                querry = Q(description__icontains=search) \
                             | Q(name__icontains=search) \
                             | Q(observation__icontains=search) \
                             | Q(recommendation__icontains=search) \
                             | Q(cve__icontains=search) \
                             | Q(levelRisk__icontains=search) \
                             | Q(service__name__icontains=search)
                if queryVulnModel:
                    queryVulnModel = queryVulnModel | querry
                else:
                    queryVulnModel = querry

        # Filter On Vuln
        else:
            search = rawSearch
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
        serviceID = kwargs.get('serviceID', None)
        if type(serviceID) is list:
            try:
                querySet = querySet.filter(service__in=serviceID)
            except (ValueError, TypeError) as e:
                return {'status': -1, 'message': "serviceID is not integer", 'detail': str(e)}
        else:
            try:
                serviceID = int(serviceID)
            except (ValueError, TypeError) as e:
                return {'status': -1, 'message': "serviceID is not integer", 'detail': str(e)}
            querySet = querySet.filter(service=serviceID)

    # Filter by project
    if 'projectID' in kwargs:
        projectID = kwargs.get('projectID', None)
        if type(projectID) is list:
            try:
                querySet = querySet.filter(ScanInfoVuln__scanTask__scanProject__in=projectID)
            except (ValueError, TypeError) as e:
                return {'status': -1, 'message': "projectID is not integer", 'detail': str(e)}
        else:
            try:
                projectID = int(kwargs.get('projectID'))
            except (ValueError, TypeError) as e:
                return {'status': -1, 'message': "projectID is not integer", 'detail': str(e)}
            querySet = querySet.filter(ScanInfoVuln__scanTask__scanProject=projectID)

    # Filter by scanTask
    if 'scanID' in kwargs:
        scanID = kwargs.get('scanID', None)
        if type(scanID) is list:
            try:
                querySet = querySet.filter(ScanInfoVuln__scanTask__in=scanID)
            except (ValueError, TypeError) as e:
                return {'status': -1, 'message': "scanID is not integer", 'detail': str(e)}
        else:
            try:
                scanID = int(scanID)
            except (ValueError, TypeError) as e:
                return {'status': -1, 'message': "scanID is not integer", 'detail': str(e)}
            querySet = querySet.filter(ScanInfoVuln__scanTask__id=scanID)

    # Filter by host
    if 'hostID' in kwargs:
        hostID = kwargs.get('hostID', None)
        if type(hostID) is list:
            try:
                querySet = querySet.filter(ScanInfoVuln__hostScanned__in=hostID)
            except (ValueError, TypeError) as e:
                return {'status': -1, 'message': "hostID is not integer", 'detail': str(e)}
        else:
            try:
                hostID = int(hostID)
            except (ValueError, TypeError) as e:
                return {'status': -1, 'message': "hostID is not integer", 'detail': str(e)}
            querySet = querySet.filter(ScanInfoVuln__hostScanned__id=hostID)

    querySet=querySet.distinct()

    # get total
    numObject = querySet.count()
    # Get sort field
    if 'sortName' in kwargs:
        sortNames = kwargs.get('sortName', None)
        sortOrder = kwargs.get('sortOrder', None)
        if type(sortNames) is list:
            sortStrings = []
            for index, sortName in enumerate(sortNames):
                if type(sortOrder) is list:
                    try:
                        if sortOrder[index] == 'asc':
                            sortString = ''
                        else:
                            sortString = '-'
                    except IndexError:
                        sortString = '-'
                elif sortOrder == 'asc':
                    sortString = ''
                else:
                    sortString = '-'
                sortString=sortString + sortName
                sortString = sortString.replace('.', '__')
                sortStrings.append(sortString)
            querySet = querySet.order_by(*sortStrings)

        else:
            if type(sortOrder) is list:
                try:
                    if sortOrder[0] == 'asc':
                        sortString = ''
                    else:
                        sortString = '-'
                except IndexError:
                    sortString = '-'
            elif sortOrder == 'asc':
                sortString = ''
            else:
                sortString = '-'
            sortString = sortString+sortNames
            sortString = sortString.replace('.', '__')
            querySet = querySet.order_by(sortString)

    # page number
    if 'pageNumber' in kwargs:
        pageNumber = kwargs.get('pageNumber', None)
        if type(pageNumber) is list:
            try:
                page = int(pageNumber[0])
            except (TypeError, IndexError) as e:
                return {'status': -1, 'message': "pageNumber is not integer", 'detail': str(e)}
        else:
            try:
                page = int(pageNumber)
            except TypeError as e:
                return {'status': -1, 'message': "pageNumber is not integer", 'detail': str(e)}
    else:
        page = PAGE_DEFAULT

    # Get Page Size
    if 'pageSize' in kwargs:
        pageSize = kwargs.get('pageSize', None)
        if type(pageSize) is list:
            try:
                numEntry = pageSize[0]
            except IndexError:
                numEntry = NUM_ENTRY_DEFAULT
        else:
            numEntry = pageSize
        # IF Page size is 'ALL'
        if numEntry.lower() == 'all' or numEntry == -1:
            numEntry = numObject
        else:
            try:
                numEntry = int(numEntry)
            except TypeError as e:
                return {'status': -1, 'message': "pageSize is not integer", 'detail': str(e)}
    else:
        numEntry = NUM_ENTRY_DEFAULT
    querySetPaged = Paginator(querySet, int(numEntry))
    dataPaged = querySetPaged.get_page(page)

    return {'status': 0, 'object': dataPaged, 'total': numObject}


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
        currentVulns = GetVulns(hostID=hostID, scanID=latestScanTask.id, pageSize= -1)['object']
        return {'status': 0, 'object': currentVulns}
    else:
        return {'status': -1, 'message': "HostID is required"}