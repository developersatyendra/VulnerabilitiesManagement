from django.utils.datastructures import MultiValueDictKeyError
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.contrib.auth.models import User
from hosts.models import HostModel
from vulnerabilities.models import VulnerabilityModel
from scans.models import ScanTaskModel, ScanInfoModel
from projects.models import ScanProjectModel
from .models import ServiceModel
from .serializers import ServiceSerializer
from .forms import ServiceForm, ServiceIDForm
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required

PAGE_DEFAULT = 1
NUM_ENTRY_DEFAULT = 50


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