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


# GetVulns get vulns from these params:
def GetVulns(*args, **kwargs,):
    vulnQuery = Q()

    # Project Filter
    projectID = kwargs.get('projectID', None)
    if projectID:
        try:
            projectID = int(projectID)
        except (ValueError, TypeError) as e:
            return {'status': -1, 'message': str(e)}
        vulnQuery = Q(ScanInfoVuln__scanTask__scanProject=projectID)

    # Scan Filter
    scanID = kwargs.get('scanID', None)
    if scanID:
        try:
            scanID = int(scanID)
        except (ValueError, TypeError) as e:
            return {'status': -1, 'message': str(e)}
        vulnQuery = vulnQuery & Q(ScanInfoVuln__scanTask=scanID)

    # Host Filter
    hostID = kwargs.get('hostID', None)
    if hostID:
        try:
            hostID = int(hostID)
        except (ValueError, TypeError) as e:
            return {'status': -1, 'message': str(e)}
        vulnQuery = vulnQuery & Q(ScanInfoVuln__hostScanned=hostID)

    # Vuln Filter
    vulnID = kwargs.get('vulnID', None)
    if vulnID:
        try:
            vulnID = int(vulnID)
        except (ValueError, TypeError) as e:
            return {'status': -1, 'message': str(e)}
        vulnQuery = vulnQuery & Q(id=vulnID)

    # Serivce Filter
    serviceID = kwargs.get('serviceID', None)
    if serviceID:
        try:
            serviceID = int(serviceID)
        except (ValueError, TypeError) as e:
            return {'status': -1, 'message': str(e)}
        vulnQuery = vulnQuery & Q(service=serviceID)

    vulns = VulnerabilityModel.objects.filter(vulnQuery).distinct()

    # Check if need for serialize
    serializer = kwargs.get('serializer', None)
    if serializer:
        serializedData = serializer(vulns, many=True)
        return {'status': 0, 'object': serializedData.data}
    return {'status': 0, 'object': vulns}


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


def GetCurrentHostVuln(*args,**kwargs):
    hostID = kwargs.get('hostID', None)
    if hostID:
        latestScanTask = ScanTaskModel.objects.filter(ScanInfoScanTask__hostScanned__id=hostID).order_by('-startTime')[0]
        currentVulns = GetVulns(hostID=hostID, scanID=latestScanTask.id)['object'].order_by('-levelRisk')
        return {'status': 0, 'object': currentVulns}
    else:
        return {'status': -1, 'message': "HostID is required"}