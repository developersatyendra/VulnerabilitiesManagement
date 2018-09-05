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
from queue import Queue
import threading
from .models import SubmitModel

HOSTDATA = "1\\XML\\en\\Host_Data.xml"
RISKDATA = "1\\XML\\en\\Risk_Data.xml"

NUM_WORKER = 15
SUBMIT_OBJ_QUEUE = Queue()

FLG_STOP = False
FLG_RESET = False


class SubmitQueueElement:
    submitObj = None   # SubmitModel object
    overwrite = False   # To determine If object is needed to OverWrite

    def __init__(self, **kwargs):
        self.submitObj = kwargs['submitObj']
        self.overwrite = kwargs['overwrite']


def ProcessFoundStoneZipXML(submitQueueElement):
    # extract zipped file
    try:
        zipFile = zipfile.ZipFile(submitQueueElement.submitObj.fileSubmitted.path, 'r')
    except OSError:
        submitQueueElement.submitObj.status = 'Error - Zip file not found'
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


def ProcessFoundStoneXML(hostdata, riskdata, submitQueueElement):

    projectID = submitQueueElement.submitObj.project
    userID = submitQueueElement.submitObj.submitter
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

    # Check If ScanTask is exis on Database
    scanTaskQuery = Q(name=rootHostData[1].attrib['ScanName'])
    scanTaskQueried = ScanTaskModel.objects.filter(scanTaskQuery)
    if scanTaskQueried:

        # If overwrite is not set. Just set status to 'duplicated'
        if not overwrite:
            submitObj.status = "Duplicated"
            submitObj.scanTask = scanTaskQueried[0]
            submitObj.save()
            return -1

        # Otherwise delete all involved scanInfo and scanTask then add new one
        scantaskObj = scanTaskQueried[0]
        scanInfoQuery = scantaskObj.scanInfo.all()
        for scanInfo in scanInfoQuery:
            scanInfo.delete()
        scantaskObj.delete()

    scantaskObj = ScanTaskModel()
    scantaskObj.name = rootHostData[1].attrib['ScanName']
    scantaskObj.startTime = DateParser.parse(rootHostData[1].attrib['StartTime'])
    scantaskObj.endTime = DateParser.parse(rootHostData[1].attrib['EndTime'])
    scantaskObj.submitter = User.objects.get(pk=1)
    scantaskObj.scanProject = ScanProjectModel.objects.get(pk=projectID)
    scantaskObj.scanBy = User.objects.get(pk=userID)
    scantaskObj.save()

    # Save Scan Task to submit
    submitObj.scanTask = scantaskObj
    submitObj.save()

    # Process Hosts
    for host in rootHostData[2]:
        # Check if this host is existed in Database
        hostQuery = Q(ipAddr=host.attrib['IPAddress'])
        hostQueried = HostModel.objects.filter(hostQuery)
        # If host does not exist in Database, Create new one
        if not hostQueried:
            hostObj = HostModel()
            hostObj.ipAddr = host.attrib['IPAddress']
            hostObj.osName = host.attrib['OSName']
            hostObj.hostName = host.attrib['NBName']
            hostObj.createBy = User.objects.get(pk=userID)
            hostObj.save()
        else:
            hostObj = hostQueried[0]

        # Create new Scan Info
        scanInfo = ScanInfoModel()
        scanInfo.hostScanned = hostObj
        scanInfo.save()

        # Process service found
        serviceFound = host[0]
        for service in serviceFound:
            # Check if this service is existed in Database
            serviceQuery = Q(name=service.attrib['ServiceName'], port=service[0].text)
            serviceQueried = ServiceModel.objects.filter(serviceQuery)

            # If it does not exist, Create new one and add to Host
            if not serviceQueried:
                serviceObj = ServiceModel()
                serviceObj.name = service.attrib['ServiceName']
                serviceObj.port = service[0].text
                serviceObj.createBy = User.objects.get(pk=userID)
                serviceObj.save()
                hostObj.services.add(serviceObj)

            # If Service is exist in Databases, Check if Service is added to Host
            else:
                serviceAdded = hostObj.services.filter(id=serviceQueried[0].id)

                # If Service is in database but not added to host, Add it to host
                if not serviceAdded:
                    hostObj.services.add(serviceQueried[0])
        hostObj.save()
        # Process vuln found
        vulnFound = host[1]
        for vuln in vulnFound:
            # Check if this vuln is existed on DB
            vulnQuery = Q(name=vuln.attrib['VulnName'])
            vulnQueried = VulnerabilityModel.objects.filter(vulnQuery)

            # If it does not exist on DB, Create new one
            if not vulnQueried:
                vulnObj = VulnerabilityModel()
                vulnObj.name = vuln.attrib['VulnName']
                vulnObj.levelRisk = vuln[0].text
                vulnObj.description = vuln[4].text
                if vuln[5]:
                    vulnObj.cve = vuln[5].text
                else:
                    vulnObj.cve = '-'
                vulnObj.service = hostObj.services.all().filter(name=vuln[1].text, port=vuln[2].text)[0]

                for vulnRisk in rootRiskData:
                    if vulnRisk.attrib['FaultlineID'] == vuln.attrib['id']:
                        vulnObj.observation = vulnRisk[2].text
                        vulnObj.recommendation = vulnRisk[3].text
                        break
                vulnObj.save()
            else:
                vulnObj = vulnQueried[0]
            scanInfo.vulnFound.add(vulnObj)
        scanInfo.save()
        scantaskObj.scanInfo.add(scanInfo)
    scantaskObj.save()
    submitObj.status = "Processed"
    submitObj.save()
    return scantaskObj


def GetResourceFromQueue(stopEvent):
    print("thread a")
    while not stopEvent.isSet():
        if not SUBMIT_OBJ_QUEUE.empty():
            submitQueueElement = SUBMIT_OBJ_QUEUE.get()
            print("Process ()".format(submitQueueElement.submitObj.fileSubmitted))
            ProcessFoundStoneZipXML(submitQueueElement)


def MgntThreadingSubmitProcess():
    
    # Whet Web App Startup. Put all Submit Objects were not processed to Queue
    submitQuery = SubmitModel.objects.filter(status='uploaded')
    for submitObj in submitQuery:
        objectQueue = SubmitQueueElement(submitObj=submitObj, overwrite=True)
        SUBMIT_OBJ_QUEUE.put(objectQueue)
        
    stop = threading.Event()
    threads = []
    for worker in range(NUM_WORKER):
        thread = threading.Thread(target=GetResourceFromQueue, args=[stop,])
        thread.daemon = True
        thread.start()
        threads.append(thread)

    print("Start All Thread")
    while True:
        # Stop All Thread
        if FLG_RESET or FLG_STOP:
            stop.set()
            # Wait for all thread is Stop
            while True:
                isAliveAll = False
                for thread_t in threads:
                    isAliveAll = isAliveAll | thread_t.isAlive()
                if not isAliveAll:
                    break
            stop.clear()
        # Start Thread Again
        if FLG_RESET:
            for thread_t in threads:
                thread_t.start()

        # Exit Function
        if FLG_STOP:
            break

