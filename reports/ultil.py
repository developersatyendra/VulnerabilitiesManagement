from django.db.models import F, Q, Count
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from datetime import datetime
from django.template.loader import get_template
from django.conf import settings
from hosts.models import HostModel
from scans.models import ScanTaskModel
from projects.models import ScanProjectModel
import tempfile
from os import path
import shutil
import pdfkit
from scans.ultil import GetScansVuln
from hosts.ultil import GetHostsVuln
from vulnerabilities.ultil import *
from .graphs import *


PATH_GEN_REPORT = getattr(settings, 'PATH_GEN_REPORT')


# High is >= LEVEL_HIGH
LEVEL_HIGH = getattr(settings, 'LEVEL_HIGH', 7)

# Med is >= LEVEL_MED AND < LEVEL_HIGH
LEVEL_MED = getattr(settings, 'LEVEL_MED', 4)

# Low is > LEVEL_INFO AND < LEVEL_MED
# Info is = LEVEL_INFO
LEVEL_INFO = getattr(settings, 'LEVEL_INFO', 0)


# Global Const for PDF coverter
MARGIN = '0.6in'
PATH_WKHTMLTOPDF = getattr(settings, 'PATH_WKHTMLTOPDF', r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

# HTML Template
TEMPLATES = {
    'cover': 'reports/pdf/cover.html',

    'host_detail_info': 'reports/pdf/host_detailed_info.html',
    'host_vulns': 'reports/pdf/host_vulns.html',

    'scan_detail_info': 'reports/pdf/scan_detailed_info.html',
    'scan_vulns': 'reports/pdf/scan_vulns.html',

    'project_detail_info': 'reports/pdf/project_detailed_info.html',
    'project_vulns': 'reports/pdf/project_vulns.html',
}
REPORT_CSS_DEFAULT = [
        path.join(getattr(settings, 'BASE_DIR'), r'static\vendor\bootstrap\css\bootstrap4.min.css'),
        path.join(getattr(settings, 'BASE_DIR'), r'static\vendor\font-awesome\css\font-awesome.css'),
]
REPORT_CSS = getattr(settings, 'REPORT_CSS', REPORT_CSS_DEFAULT)
REPORT_LOGO = getattr(settings, 'REPORT_LOGO')


def ConvertHTMLToPDF(htmlPaths, coverPath):
    config = pdfkit.configuration(wkhtmltopdf=PATH_WKHTMLTOPDF)

    options = {
        'quiet': '',
        'page-size': 'A4',
        # 'margin-top': MARGIN,
        # 'margin-right': MARGIN,
        # 'margin-bottom': MARGIN,
        # 'margin-left': MARGIN,
        # 'disable-smart-shrinking': '',
        'footer-center': 'Page [page]',
        'header-right': '[section]',
        'enable-javascript': False,
    }
    toc = {
        'toc-header-text': 'Table Of Contents'
    }
    if coverPath:
        try:
            content = pdfkit.from_file(htmlPaths, False, configuration=config, cover=coverPath, toc=toc, cover_first=True, options=options)
        except IOError as errorMsg:
            return {'status': -1, 'message': errorMsg}
        return {'status': 0, 'object': content}
    else:
        try:
            content = pdfkit.from_file(htmlPaths, False, configuration=config, toc=toc, cover_first=True, options=options)
        except IOError as errorMsg:
            return {'status': -1, 'message': errorMsg}
        return {'status': 0, 'object': content}


def PDFHostReport(report):

    # Create temporary dir
    tempdir = tempfile.mkdtemp()

    try:
        host = report.host

    # In case Host with ID does not exist
    except HostModel.DoesNotExist:
        shutil.rmtree(tempdir)
        return {'status': -1, 'message': 'Host Does Not Exist'}

    #######################################
    # Render Cover page

    htmlTemplate = get_template(TEMPLATES['cover'])
    username = report.createBy.username
    context = {
        'css': REPORT_CSS,
        'img_logo': REPORT_LOGO,
        'username': username,
        'report_name': 'Host Vulnerabilities Report',
        'time_generate': datetime.now(),
        'host': host
    }
    html = htmlTemplate.render(context)
    coverFilePath = path.join(tempdir, 'cover.html')
    coverFile = open(coverFilePath, 'wb')
    coverFile.write(html.encode())
    coverFile.close()

    #######################################
    # Render Host Detailed Info

    htmlTemplate = get_template(TEMPLATES['host_detail_info'])
    services = host.services.all()
    context = {
        'css': REPORT_CSS,
        'host': host,
        'services': services,
    }
    html = htmlTemplate.render(context)
    hostinfoFilePath = path.join(tempdir, 'host_info.html')
    File = open(hostinfoFilePath, 'wb')
    File.write(html.encode())
    File.close()

    #######################################
    # Render Host vulns

    htmlTemplate = get_template(TEMPLATES['host_vulns'])

    scanVuln = GetScansVuln(hostID=host.id)['object']
    vulns = GetCurrentHostVuln(hostID=host.id)['object']

    # Get statistic vuln by service
    statVulnHostSrv = VulnStatisticByService(hostID=host.id)
    serviceName = []
    serviceVuln = []
    result = sorted(statVulnHostSrv.items(), key=lambda t: t[1], reverse=True)
    for name, vuln in result:
        serviceName.append(name)
        serviceVuln.append(vuln)
    graph_serivce = RenderDonutChart(serviceVuln, serviceName)

    # categorize vulns by group high, med, low, info
    categorizeVuln = []
    categorizeVuln.append(vulns.filter(Q(levelRisk__gte=LEVEL_HIGH)).count())
    categorizeVuln.append(vulns.filter(Q(levelRisk__gte=LEVEL_MED) & Q(levelRisk__lt=LEVEL_HIGH)).count())
    categorizeVuln.append(vulns.filter(Q(levelRisk__gt=LEVEL_INFO) & Q(levelRisk__lt=LEVEL_MED)).count())
    categorizeVuln.append(vulns.filter(Q(levelRisk=LEVEL_INFO)).count())
    graph_vuln = RenderBarChart(categorizeVuln, ['High', 'Med', 'Low', 'Info'], 'Vulnerabilities')

    # Get scan history graph
    scanname = []
    high_t = []
    med_t = []
    low_t = []
    info_t = []
    for scan in scanVuln:
        scanname.append(scan.name)
        info_t.append(scan.info)
        low_t.append(scan.low)
        med_t.append(scan.med)
        high_t.append(scan.high)
    vulnData = []
    vulnData.append(info_t)
    vulnData.append(low_t)
    vulnData.append(med_t)
    vulnData.append(high_t)

    graph_scan_history = RenderStackBarChart(vulnData, labels=['High', 'Medium', 'Low', 'Info'], xticks=scanname, labely='Vulnerabilities')
    # Fill values to template
    context = {
        'css': REPORT_CSS,
        'scantasks': scanVuln,
        'graph_vuln': graph_vuln,
        'graph_serivce': graph_serivce,
        'graph_scan_history': graph_scan_history,
        'vulns': vulns
    }
    html = htmlTemplate.render(context)
    hostvulnsFilePath = path.join(tempdir, 'host_vulns.html')
    File = open(hostvulnsFilePath, 'wb')
    File.write(html.encode())
    File.close()
    reportPath = path.join(PATH_GEN_REPORT, report.name + '.pdf')
    retval = ConvertHTMLToPDF([hostinfoFilePath, hostvulnsFilePath], coverFilePath)
    shutil.rmtree(tempdir)
    if retval['status'] == -1:
        return retval
    else:
        # Assign file path of report
        report.fileReport.save(report.name+'.pdf', ContentFile(retval['object']))
        report.save()
    return {'status': 0, 'object': report}


def PDFScanReport(report):
    # Create temporary dir
    tempdir = tempfile.mkdtemp()

    try:
        scan = report.scanTask

    # In case Host with ID does not exist
    except ScanTaskModel.DoesNotExist:
        shutil.rmtree(tempdir)
        return {'status': -1, 'message': 'Scan Task Does Not Exist'}

    #######################################
    # Render Cover page

    htmlTemplate = get_template(TEMPLATES['cover'])
    username = report.createBy.username
    context = {
        'css': REPORT_CSS,
        'img_logo': REPORT_LOGO,
        'username': username,
        'report_name': 'Scan Task Vulnerabilities Report',
        'time_generate': datetime.now(),
        'scan': scan
    }
    html = htmlTemplate.render(context)
    coverFilePath = path.join(tempdir, 'cover.html')
    coverFile = open(coverFilePath, 'wb')
    coverFile.write(html.encode())
    coverFile.close()

    #######################################
    # Render Scan Detailed Info

    htmlTemplate = get_template(TEMPLATES['scan_detail_info'])
    context = {
        'css': REPORT_CSS,
        'scan': scan,
    }
    html = htmlTemplate.render(context)
    scaninfoFilePath = path.join(tempdir, 'scan_info.html')
    File = open(scaninfoFilePath, 'wb')
    File.write(html.encode())
    File.close()

    #######################################
    # Render scan vulnerabilities

    # Template
    htmlTemplate = get_template(TEMPLATES['scan_vulns'])

    # Get Vulnerbilities were discovered by this scan
    vulns = GetVulns(scanID=scan.id)['object']

    # Get statistic vuln by service
    statVulnScanSrv = VulnStatisticByService(scanID=scan.id)
    serviceName = []
    serviceVuln = []
    result = sorted(statVulnScanSrv.items(), key=lambda t: t[1], reverse=True)
    for name, vuln in result:
        serviceName.append(name)
        serviceVuln.append(vuln)
    graph_serivce = RenderDonutChart(serviceVuln, serviceName)

    # Get statistic vuln by OS
    statVulnScanOS = VulnStatisticByOS(scanID=scan.id)
    osName = []
    osVuln = []
    result = sorted(statVulnScanOS.items(), key=lambda t: t[1], reverse=True)
    for name, vuln in result:
        osName.append(name)
        osVuln.append(vuln)
    graph_os = RenderDonutChart(osVuln, osName)

    # categorize vulns by group high, med, low, info
    categorizeVuln = []
    categorizeVuln.append(vulns.filter(Q(levelRisk__gte=LEVEL_HIGH)).count())
    categorizeVuln.append(vulns.filter(Q(levelRisk__gte=LEVEL_MED) & Q(levelRisk__lt=LEVEL_HIGH)).count())
    categorizeVuln.append(vulns.filter(Q(levelRisk__gt=LEVEL_INFO) & Q(levelRisk__lt=LEVEL_MED)).count())
    categorizeVuln.append(vulns.filter(Q(levelRisk=LEVEL_INFO)).count())
    graph_vuln = RenderBarChart(categorizeVuln, ['High', 'Med', 'Low', 'Info'], 'Vulnerabilities')

    # Get graph_scan_result
    hostvulns = GetHostsVuln(scanID=scan.id)['object']

    ipAddress = []
    high_t = []
    med_t = []
    low_t = []
    info_t = []
    for hostvuln in hostvulns:
        ipAddress.append(hostvuln.ipAddr)
        info_t.append(hostvuln.info)
        low_t.append(hostvuln.low)
        med_t.append(hostvuln.med)
        high_t.append(hostvuln.high)
    vulnData = []
    vulnData.append(info_t)
    vulnData.append(low_t)
    vulnData.append(med_t)
    vulnData.append(high_t)

    graph_scan_result = RenderStackBarChart(vulnData, labels=['High', 'Medium', 'Low', 'Info'], xticks=ipAddress,
                                             labely='Vulnerabilities')

    # Get vuln by host
    hostIDs = scan.ScanInfoScanTask.values_list('hostScanned')
    host_t = HostModel.objects.filter(id__in=hostIDs)
    vuln_t = []
    for host in host_t:
        vuln_t.append(GetVulns(hostID=host.id, scanID=scan.id, sortName='levelRisk', sortOrder='desc')['object'])
    # Fill values to template
    context = {
        'css': REPORT_CSS,                              # CSS - Bootstrap
        'graph_OS': graph_os,                           # img base64 - Graph Vuln by OS
        'graph_serivce': graph_serivce,                 # img base64 - Graph Vuln by services
        'graph_vuln': graph_vuln,                       # img base64 - Graph Total Vuln of Scan
        'graph_scan_result': graph_scan_result,         # img base64 - Graph Result of Scan
        'hostvulns': hostvulns,                         # Scan Reults table
        'hosts': host_t,
        'vulnByHost': vuln_t,                           # Vulns by host
        'vulns': vulns                                  # vulns in detailed
    }
    html = htmlTemplate.render(context)
    scanvulnsFilePath = path.join(tempdir, 'host_vulns.html')
    File = open(scanvulnsFilePath, 'wb')
    File.write(html.encode())
    File.close()
    reportPath = path.join(PATH_GEN_REPORT, report.name + '.pdf')
    retval = ConvertHTMLToPDF([scaninfoFilePath, scanvulnsFilePath], coverFilePath)
    shutil.rmtree(tempdir)
    if retval['status'] == -1:
        return retval
    else:
        # Assign file path of report
        report.fileReport.save(report.name+'.pdf', ContentFile(retval['object']))
        report.save()
    return {'status': 0, 'object': report}


def PDFProjectReport(report):
    # Create temporary dir
    tempdir = tempfile.mkdtemp()

    try:
        project = report.scanProject

    # In case Host with ID does not exist
    except ScanProjectModel.DoesNotExist:
        shutil.rmtree(tempdir)
        return {'status': -1, 'message': 'Project Does Not Exist'}

    #######################################
    # Render Cover page

    htmlTemplate = get_template(TEMPLATES['cover'])
    username = report.createBy.username
    context = {
        'css': REPORT_CSS,
        'img_logo': REPORT_LOGO,
        'username': username,
        'report_name': 'Project Vulnerabilities Report',
        'time_generate': datetime.now(),
        'project': project
    }
    html = htmlTemplate.render(context)
    coverFilePath = path.join(tempdir, 'cover.html')
    coverFile = open(coverFilePath, 'wb')
    coverFile.write(html.encode())
    coverFile.close()

    #######################################
    # Render Project Detailed Info

    htmlTemplate = get_template(TEMPLATES['project_detail_info'])
    context = {
        'css': REPORT_CSS,
        'project': project,
    }
    html = htmlTemplate.render(context)
    projectinfoFilePath = path.join(tempdir, 'project_info.html')
    File = open(projectinfoFilePath, 'wb')
    File.write(html.encode())
    File.close()

    #######################################
    # Render scan vulnerabilities

    # Template
    htmlTemplate = get_template(TEMPLATES['project_vulns'])

    # Get Vulnerbilities were discovered by this scan
    vulns = GetVulns(projectID=project.id)['object']

    # Get statistic vuln by service
    statVulnScanSrv = VulnStatisticByService(projectID=project.id)
    serviceName = []
    serviceVuln = []
    result = sorted(statVulnScanSrv.items(), key=lambda t: t[1], reverse=True)
    for name, vuln in result:
        serviceName.append(name)
        serviceVuln.append(vuln)
    graph_serivce = RenderDonutChart(serviceVuln, serviceName)

    # Get statistic vuln by OS
    statVulnScanOS = VulnStatisticByOS(projectID=project.id)
    osName = []
    osVuln = []
    result = sorted(statVulnScanOS.items(), key=lambda t: t[1], reverse=True)
    for name, vuln in result:
        osName.append(name)
        osVuln.append(vuln)
    graph_os = RenderDonutChart(osVuln, osName)

    # categorize vulns by group high, med, low, info
    categorizeVuln = []
    categorizeVuln.append(vulns.filter(Q(levelRisk__gte=LEVEL_HIGH)).count())
    categorizeVuln.append(vulns.filter(Q(levelRisk__gte=LEVEL_MED) & Q(levelRisk__lt=LEVEL_HIGH)).count())
    categorizeVuln.append(vulns.filter(Q(levelRisk__gt=LEVEL_INFO) & Q(levelRisk__lt=LEVEL_MED)).count())
    categorizeVuln.append(vulns.filter(Q(levelRisk=LEVEL_INFO)).count())
    graph_vuln = RenderBarChart(categorizeVuln, ['High', 'Med', 'Low', 'Info'], 'Vulnerabilities')

    # Get graph_scan_result
    scanvulns = GetScansVuln(projectID=project.id)['object']

    scanName = []
    high_t = []
    med_t = []
    low_t = []
    info_t = []
    for scanvuln in scanvulns:
        scanName.append(scanvuln.name)
        info_t.append(scanvuln.info)
        low_t.append(scanvuln.low)
        med_t.append(scanvuln.med)
        high_t.append(scanvuln.high)
    vulnData = []
    vulnData.append(info_t)
    vulnData.append(low_t)
    vulnData.append(med_t)
    vulnData.append(high_t)

    graph_vulns_by_scan = RenderStackBarChart(vulnData, labels=['High', 'Medium', 'Low', 'Info'], xticks=scanName,
                                            labely='Vulnerabilities')

    # Get vuln by host
    host_t = HostModel.objects.filter(ScanInfoHost__scanTask__scanProject=project).annotate(
        high=Count('services'),
        med=Count('services'),
        low=Count('services'),
        info=Count('services'),
    )
    for host in host_t:
        latestScanTask = ScanTaskModel.objects.filter(ScanInfoScanTask__hostScanned__id=host.id).order_by('-startTime')[0]
        currentVuln = GetVulns(hostID=host.id, scanID=latestScanTask.id, sortName='levelRisk', sortOrder='desc')['object']
        currentVuln = currentVuln.aggregate(
            high=Count('id', filter=Q(levelRisk__gte=LEVEL_HIGH), distinct=True),
            med=Count('id', filter=(Q(levelRisk__gte=LEVEL_MED)&Q(levelRisk__lt=LEVEL_HIGH)),distinct=True),
            low=Count('id', filter=Q(levelRisk__gt=LEVEL_INFO)&Q(levelRisk__lt=LEVEL_MED), distinct=True),
            info=Count('id', filter=Q(levelRisk=LEVEL_INFO), distinct=True),
        )
        host.high = currentVuln['high']
        host.med = currentVuln['med']
        host.low = currentVuln['low']
        host.info = currentVuln['info']
    host_t = sorted(host_t, key=lambda x: (x.high, x.med, x.low, x.info), reverse=True)

    # Fill values to template
    context = {
        'css': REPORT_CSS,                               # CSS - Bootstrap
        'graph_OS': graph_os,                            # img base64 - Graph Vuln by OS
        'graph_serivce': graph_serivce,                  # img base64 - Graph Vuln by services
        'graph_vuln': graph_vuln,                        # img base64 - Graph Total Vuln of Scan
        'graph_vulns_by_scan': graph_vulns_by_scan,      # img base64 - vuln by scan graph
        'scanvulns': scanvulns,                          # vulns by scan
        'hosts': host_t,                                 # vulns by host
        'vulns': vulns                                   # vulns in detailed
    }
    html = htmlTemplate.render(context)
    projectvulnsFilePath = path.join(tempdir, 'project_vulns.html')
    File = open(projectvulnsFilePath, 'wb')
    File.write(html.encode())
    File.close()
    reportPath = path.join(PATH_GEN_REPORT, report.name+'.pdf')
    retval = ConvertHTMLToPDF([projectinfoFilePath, projectvulnsFilePath], coverFilePath)
    shutil.rmtree(tempdir)
    if retval['status'] == -1:
        return retval
    else:
        # Assign file path of report
        report.fileReport.save(report.name+'.pdf', ContentFile(retval['object']))
        report.save()
    return {'status': 0, 'object': report}