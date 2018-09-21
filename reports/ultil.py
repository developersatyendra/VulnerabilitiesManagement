from django.shortcuts import render
from django.contrib.auth.models import User
from datetime import datetime
from django.template.loader import get_template
from django.conf import settings
from hosts.models import HostModel
import tempfile
from os import path
import shutil
import pdfkit
from scans.ultil import GetScansVuln
from vulnerabilities.ultil import GetCurrentHostVuln

# Global Const for PDF coverter
MARGIN = '0.6in'
PATH_WKHTMLTOPDF = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'

# HTML Template
TEMPLATES = {
    'cover': 'reports/pdf/cover.html',
    'host_detail_info': 'reports/pdf/host_detailed_info.html',
    'host_vulns': 'reports/pdf/host_vulns.html',
}

CSS = path.join(getattr(settings, 'BASE_DIR'), r'static\vendor\bootstrap\css\bootstrap4.min.css')
LOGO = path.join(getattr(settings, 'BASE_DIR'), r'media\img\reports\logo.png')


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
        return pdfkit.from_file(htmlPaths, 'D:/output.pdf', configuration=config, cover=coverPath, toc=toc, cover_first=True, options=options)
    else:
        return pdfkit.from_file(htmlPaths, 'D:/output.pdf', configuration=config, toc=toc, cover_first=True, options=options)


def PDFHostReport(hostID, reportID):
    # Create temporary dir
    tempdir = tempfile.mkdtemp()

    try:
        host = HostModel.objects.get(pk=hostID)

    # In case Host with ID does not exist
    except HostModel.DoesNotExist:
        shutil.rmtree(tempdir)
        return -1

    # Render Cover page
    htmlTemplate = get_template(TEMPLATES['cover'])
    username = User.objects.get(pk=1).username
    context = {
        'css': CSS,
        'img_logo': LOGO,
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

    # Render Host Detailed Info
    htmlTemplate = get_template(TEMPLATES['host_detail_info'])
    services = host.services.all()
    context = {
        'css': CSS,
        'host': host,
        'services': services,
    }
    html = htmlTemplate.render(context)
    hostinfoFilePath = path.join(tempdir, 'host_info.html')
    File = open(hostinfoFilePath, 'wb')
    File.write(html.encode())
    File.close()

    # Render Host vulns
    htmlTemplate = get_template(TEMPLATES['host_vulns'])

    scanVuln = GetScansVuln(hostID=hostID)['object']
    vulns = GetCurrentHostVuln(hostID=hostID)['object']
    context = {
        'css': CSS,
        'scantasks': scanVuln,
        'vulns': vulns
    }
    html = htmlTemplate.render(context)
    hostvulnsFilePath = path.join(tempdir, 'host_vulns.html')
    File = open(hostvulnsFilePath, 'wb')
    File.write(html.encode())
    File.close()

    ConvertHTMLToPDF([hostinfoFilePath, hostvulnsFilePath], coverFilePath)

    return 0