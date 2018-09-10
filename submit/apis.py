from os import remove
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.paginator import Paginator
from .serializers import SubmitSerializer
from .forms import SubmitAddForm, SubmitIDForm
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
from django.db.utils import IntegrityError

import tempfile
import zipfile
from os import path
import shutil
import xml.etree.ElementTree as XMLTree
from django.db.models import Q
from scans.models import ScanTaskModel, ScanInfoModel
from projects.models import ScanProjectModel
from hosts.models import HostModel
from services.models import ServiceModel
from vulnerabilities.models import VulnerabilityModel
import dateutil.parser as DateParser
from django.contrib.auth.models import User
from .models import SubmitModel
from .tasks import ProcessSubmitFileTask


PAGE_DEFAULT = 1
NUM_ENTRY_DEFAULT = 50


HOSTDATA = "1\\XML\\en\\Host_Data.xml"
RISKDATA = "1\\XML\\en\\Risk_Data.xml"


FLG_STOP = False
FLG_RESET = False


# Class contain Submit and Overwrite flag. Play role element of Queue
class SubmitQueueElement:
    submitObj = None  # SubmitModel object
    overwrite = False  # To determine If object is needed to OverWrite

    def __init__(self, **kwargs):
        self.submitObj = kwargs['submitObj']
        self.overwrite = kwargs['overwrite']


#
# APIGetVulns get vulns from these params:
#   searchText: Search content
#   sortName: Name of column is applied sort
#   sortOrder: sort entry by order 'asc' or 'desc'
#   pageSize: number of entry per page
#   pageNumber: page number of curent view

class APIGetSubmits(APIView):
    def get(self, request):
        # Filter by search keyword
        if request.GET.get('search'):
            search = request.GET.get('search')
            # Query on ScanModel
            queryScanModel = Q(name__icontains=search)
            scanTaskPK = ScanTaskModel.objects.filter(queryScanModel).values_list('pk', flat=True)

            # Filter On Vuln
            queryVulnModel = Q(description__icontains=search)\
                             | Q(fileSubmitted__icontains=search)\
                             | Q(dateCreated__icontains=search) \
                             | Q(status__icontains=search) \
                             | Q(scanTask__in=scanTaskPK)
            querySet = SubmitModel.objects.filter(queryVulnModel)
        else:
            querySet = SubmitModel.objects.all()
        numObject = querySet.count()
        # Get sort order
        if request.GET.get('order') == 'asc':
            sortString = ''
        else:
            sortString = '-'

        # Get sort filed
        if request.GET.get('sort'):
            sortString = sortString + request.GET.get('sort')
        else:
            sortString = sortString + 'id'
        sortString = sortString.replace('.', '__')
        querySet = querySet.order_by(sortString)
        # Get Page Number
        if request.GET.get('offset'):
            page = request.GET.get('offset')
        else:
            page = PAGE_DEFAULT

        # Get Page Size
        if request.GET.get('limit'):
            numEntry = request.GET.get('limit')
            # IF Page size is 'ALL'
            if numEntry.lower() == 'all' or numEntry == -1:
                numEntry = numObject
        else:
            numEntry = NUM_ENTRY_DEFAULT
        querySetPaged = Paginator(querySet, int(numEntry))
        dataPaged = querySetPaged.get_page(page)
        dataSerialized = SubmitSerializer(dataPaged, many=True)
        data = dict()
        data["total"] = numObject
        data['rows'] = dataSerialized.data
        return Response({'status': '0', 'object': data})


# APIAddSubmit add new Submit
# return {'retVal': '-1'} if id not found
# return Submit object if it's success
#

class APIAddSubmit(APIView):
    parser_classes = (MultiPartParser, FormParser, FileUploadParser,)

    def post(self, request):
        submitForm = SubmitAddForm(request.POST, request.FILES)
        if submitForm.is_valid():
            submitObj = submitForm.save(commit=False)
            submitObj.submitter = User.objects.get(pk=1)
            submitObj.status = 'Uploaded'
            submitObj.save()
            ProcessSubmitFileTask.delay(id=submitObj.id, overwrite=False)
            dataSerialized = SubmitSerializer(submitObj, many=False)
            return Response({'status': '0', 'object': dataSerialized.data})
        else:
            return Response({'status': '-1', 'message': 'Form is invalid', 'detail': submitForm.errors})


#
# APIDeleteSubmit delete existing submit
# return {'retVal': '-1'} if id not found
# return {'retVal': 'Num of Success on Deleting'} if it's success
#

class APIDeleteSubmit(APIView):

    def post(self, request):
        submitForm = SubmitIDForm(request.POST)
        if submitForm.is_valid():
            successOnDelete = 0
            for rawID in submitForm.data['id'].split(','):
                try:
                    id = int(rawID)
                except ValueError:
                    pass
                else:
                    try:
                        retVuln = SubmitModel.objects.get(pk=id)
                    except ServiceModel.DoesNotExist:
                        pass
                    else:
                        try:
                            remove(retVuln.fileSubmitted.path)
                        except OSError:
                            pass
                        retVuln.delete()
                        successOnDelete = successOnDelete + 1
            if successOnDelete==1:
                return Response(
                    {'status': '0', 'message': '1 submit file is successfully deleted.', 'numDeleted': successOnDelete})
            else:
                return Response(
                            {'status': '0', 'message': '{} submit files are successfully deleted.'.format(successOnDelete), 'numDeleted': successOnDelete})
        else:
            return Response({'status': '-1', 'message': 'Form is invalid', 'detail': {submitForm.errors}})


#
# ProcessFoundStoneZipXML get submitQueueElement then extract zip files by path in submitobj
#

def ProcessFoundStoneZipXML(submitQueueElement):

    # Change Status tu Processing
    submitQueueElement.submitObj.status = 'Processing'
    submitQueueElement.submitObj.save()

    # extract zipped file
    try:
        zipFile = zipfile.ZipFile(submitQueueElement.submitObj.fileSubmitted.path, 'r')
    except OSError:
        submitQueueElement.submitObj.status = 'Error - Zip file not found'
        submitQueueElement.submitObj.save()
        return -1
    except zipfile.BadZipFile:
        submitQueueElement.submitObj.status = 'Submit is not Zip File'
        submitQueueElement.submitObj.save()
        return -1
    tempdir = tempfile.mkdtemp()
    try:
        zipFile.extractall(tempdir)
    except zipfile.BadZipFile:
        submitQueueElement.submitObj.status = 'Error - Extract error'
        submitQueueElement.submitObj.save()
        return -1
    zipFile.close()
    retVal = ProcessFoundStoneXML(path.join(tempdir, HOSTDATA), path.join(tempdir, RISKDATA), submitQueueElement)
    shutil.rmtree(tempdir)
    return retVal


#
# Covert XML to information and store it in to database objects
#

def ProcessFoundStoneXML(hostdata, riskdata, submitQueueElement):
    projectID = submitQueueElement.submitObj.project.id
    userID = submitQueueElement.submitObj.submitter.id
    submitObj = submitQueueElement.submitObj
    overwrite = submitQueueElement.overwrite

    # Parse XML HostaData file
    try:
        xmltreeHostData = XMLTree.parse(hostdata)
        xmltreeRiskData = XMLTree.parse(riskdata)
    except OSError:
        submitObj.status = 'Error - XML files not found'
        submitObj.save()
        return -1
    except XMLTree.ParseError:
        submitObj.status = 'Error - XML parsed error'
        submitObj.save()
        return -1
    rootHostData = xmltreeHostData.getroot()
    rootRiskData = xmltreeRiskData.getroot()[2]

    # Process ScanTasks
    scantaskObj = ScanTaskModel()
    scantaskObj.name = rootHostData[1].attrib['ScanName']
    scantaskObj.startTime = DateParser.parse(rootHostData[1].attrib['StartTime'])
    scantaskObj.endTime = DateParser.parse(rootHostData[1].attrib['EndTime'])
    scantaskObj.submitter = User.objects.get(pk=1)
    scantaskObj.scanProject = ScanProjectModel.objects.get(pk=projectID)
    scantaskObj.scanBy = User.objects.get(pk=userID)
    try:
        scantaskObj.save()

    # If scanTask has already existed on database. Check overwrite flag
    except IntegrityError:
        scanTaskConflict = ScanTaskModel.objects.get(name=rootHostData[1].attrib['ScanName'])
        if overwrite:
            scanTaskConflict.delete()
            scantaskObj.save()
        else:
            submitObj.status = "Duplicated"
            submitObj.save()
            return -1


    # Save Scan Task to submit
    submitObj.scanTask = scantaskObj
    submitObj.save()

    # Process Hosts
    for host in rootHostData[2]:
        hostObj = HostModel()
        hostObj.ipAddr = host.attrib['IPAddress']
        hostObj.osName = host.attrib['OSName']
        hostObj.hostName = host.attrib['NBName']
        hostObj.createBy = User.objects.get(pk=userID)
        try:
            hostObj.save()

        # If Host has already existed.
        except IntegrityError:
            hostObj = HostModel.objects.get(ipAddr=host.attrib['IPAddress'])


        # Create new Scan Info
        scanInfo = ScanInfoModel()
        scanInfo.hostScanned = hostObj
        scanInfo.scanTask = scantaskObj
        scanInfo.save()

        # Process service found
        serviceFound = host[0]
        for service in serviceFound:
            serviceObj = ServiceModel()
            serviceObj.name = service.attrib['ServiceName']
            serviceObj.port = service[0].text
            serviceObj.createBy = User.objects.get(pk=userID)
            try:
                serviceObj.save()
            # If this service has already existed in Database
            except IntegrityError:
                serviceQuery = Q(name=service.attrib['ServiceName'], port=service[0].text)
                serviceObj = ServiceModel.objects.filter(serviceQuery)[0]
            # Check if service has already added to host
            if not hostObj.services.filter(id=serviceObj.id):
                hostObj.services.add(serviceObj)
        # Save Host
        hostObj.save()

        # Process vuln found
        vulnFound = host[1]
        for vuln in vulnFound:
            vulnObj = VulnerabilityModel()
            vulnObj.name = vuln.attrib['VulnName']
            vulnObj.levelRisk = vuln[0].text
            vulnObj.description = vuln[4].text
            try:
                vulnObj.cve = vuln[5].text
            except IndexError:
                vulnObj.cve = '-'
            vulnObj.service = hostObj.services.all().filter(name=vuln[1].text, port=vuln[2].text)[0]
            for vulnRisk in rootRiskData:
                if vulnRisk.attrib['FaultlineID'] == vuln.attrib['id']:
                    vulnObj.observation = vulnRisk[2].text
                    vulnObj.recommendation = vulnRisk[3].text
                    break
            try:
                vulnObj.save()

            # If Vuln has already existed on DB
            except IntegrityError:
                vulnQuery = Q(name=vuln.attrib['VulnName'])
                vulnObj = VulnerabilityModel.objects.get(vulnQuery)

            scanInfo.vulnFound.add(vulnObj)
        scanInfo.save()
    submitObj.status = "Processed"
    submitObj.save()
    return scantaskObj
