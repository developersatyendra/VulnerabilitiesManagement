from django.shortcuts import render
from django.views.generic import TemplateView
from dashboard.views import RenderSideBar
from django.http import HttpResponse
from django.contrib.auth.models import User
from datetime import datetime
from django.template.loader import get_template
from django.conf import settings
from hosts.models import HostModel
from services.models import ServiceModel
import tempfile
from os import path
from .ultil import ConvertHTMLToPDF

def PDFHostReport(TemplateView):
    template = 'reports/pdf/cover.html'
    # css = path.join(r'D:\pythonProject\ReportPDF', r'bootstrap.min.css')
    css = path.join(getattr(settings, 'BASE_DIR'), r'static\vendor\bootstrap\css\bootstrap4.min.css')
    logo = path.join(getattr(settings, 'BASE_DIR'), r'media\img\reports\logo.png')

    def get(self, request, *args, **kwargs):
        tempdir = tempfile.mkdtemp()
        print(tempdir)
        print(self.css)
        htmlTemplate = get_template(self.template)
        username = User.objects.get(pk=1).username
        context = {
            'css': self.css,
            'img_logo': self.logo,
            'username':username,
            'report_name':'Vulnerabilities Report',
            'time_generate': datetime.now()
        }
        html = htmlTemplate.render(context)
        coverFilePath = path.join(tempdir, 'cover.html')
        coverFile = open(coverFilePath, 'wb')
        coverFile.write(html.encode())
        coverFile.close()

        htmlTemplate = get_template('reports/pdf/host_detailed_info.html')
        host = HostModel.objects.get(pk=1)
        services = host.services.all()
        context = {
            'css': self.css,
            'host': host,
            'services': services,
        }
        html = htmlTemplate.render(context)
        hostinfoFilePath = path.join(tempdir, 'host_info.html')
        File = open(hostinfoFilePath, 'wb')
        File.write(html.encode())
        File.close()

        ConvertHTMLToPDF([hostinfoFilePath],coverFilePath)

        return render(request, self.template, context)