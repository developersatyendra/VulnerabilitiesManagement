import tempfile
from zipfile import ZipFile
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

hostData = "1\\XML\\en\\Host_Data.xml"
riskData = "1\\XML\\en\\Risk_Data.xml"


def ProcessFoundStoneZipXML(submibObj, projectID):
    print(projectID)
    # extract zipped file
    zipFile = ZipFile(submibObj.fileSubmitted.path, 'r')
    tempdir = tempfile.mkdtemp()
    zipFile.extractall(tempdir)
    zipFile.close()
    print(path.join(tempdir, hostData))
    print(path.join(tempdir, riskData))
    retVal = ProcessFoundStoneXML(path.join(tempdir, hostData), path.join(tempdir, riskData), submibObj, projectID, 1)
    shutil.rmtree(tempdir)
    return retVal


def ProcessFoundStoneXML(hostdata, riskdata, submitObj, projectID, userID):
    # Parse XML HostaData file
    xmltreeHostData = XMLTree.parse(hostdata)
    rootHostData = xmltreeHostData.getroot()
    xmltreeRiskData = XMLTree.parse(riskdata)
    rootRiskData = xmltreeRiskData.getroot()[2]

    # Check If ScanTask is exis on Database
    scanTaskQuery = Q(name=rootHostData[1].attrib['ScanName'])
    scanTaskQueried = ScanTaskModel.objects.filter(scanTaskQuery)
    if scanTaskQueried:
        submitObj.status = "Duplicated"
        submitObj.scanTask = scanTaskQueried[0]
        return -1
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
