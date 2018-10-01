from rest_framework.views import APIView
from django.http import HttpResponse
from .models import ReportModel
from .forms import ReportForm
from .serializers import ReportSerializer
from .tasks import ProcessGenerateReportTask
from django.db.models import Q, Count, F
from django.contrib.auth.models import User
from rest_framework.response import Response
from django.core.paginator import Paginator
from wsgiref.util import FileWrapper
from os import remove

PAGE_DEFAULT = 1
NUM_ENTRY_DEFAULT = 50


######################################################
#   APIGetHostName get Name of Host from id
#
#   APIGetReports(mode, [projectID, scanID, hostID], [searchText], [sortName], [sortOrder])
class APIGetReports(APIView):

    def get(self, request):
        # Get mode value and define query
        if request.GET.get('mode'):
            try:
                mode = int(request.GET.get('mode'))
            except ValueError:
                return Response({'status': -1, 'message': "mode is not integer"})
            if mode == ReportModel.MODE_PROJECT:
                reportQuery = ReportModel.objects.filter(mode=ReportModel.MODE_PROJECT)
            elif mode == ReportModel.MODE_SCANTASK:
                reportQuery = ReportModel.objects.filter(mode=ReportModel.MODE_SCANTASK)
            elif mode == ReportModel.MODE_HOST:
                reportQuery = ReportModel.objects.filter(mode=ReportModel.MODE_HOST)
            else:
                return Response({'status': -1, 'message': "mode has improper value"})
        else:
            return Response({'status': -1, 'message': "mode is required"})

        # Filter by projectID or scanID or hostID
        if request.GET.get('projectID'):
            try:
                projectID = int(request.GET.get('projectID'))
            except ValueError:
                return Response({'status': -1, 'message': "projectID is not integer"})
            reportQuery = reportQuery.filter(scanProject=projectID)
        elif request.GET.get('scanID'):
            try:
                scanID = int(request.GET.get('scanID'))
            except ValueError:
                return Response({'status': -1, 'message': "scanID is not integer"})
            reportQuery = reportQuery.filter(scanTask=scanID)
        elif request.GET.get('hostID'):
            try:
                hostID = int(request.GET.get('hostID'))
            except ValueError:
                return Response({'status': -1, 'message': "hostID is not integer"})
            reportQuery = reportQuery.filter(host=hostID)
        reportQuery = reportQuery.distinct()

        if request.GET.get('searchText'):
            search = request.GET.get('searchText')
            query = Q(name__icontains=search)\
                    | Q(scanProject__name__icontains=search)\
                    | Q(scanTask__name__icontains=search)\
                    | Q(host__hostName__icontains=search) \
                    | Q(host__ipAddr__icontains=search)
            reportQuery = reportQuery.filter(query)

        # Get total
        numObject = reportQuery.count()

        # Get sort order
        if request.GET.get('sortOrder') == 'asc':
            sortString = ''
        else:
            sortString = '-'

        # Get sort filed
        if request.GET.get('sortName'):
            sortString = sortString + request.GET.get('sortName')
            sortString = sortString.replace('.', '__')
            sortString = [sortString]
        else:
            sortString = ['-dateUpdate']
        querySet = reportQuery.order_by(*sortString)

        # Get Page Number
        if request.GET.get('pageNumber'):
            page = request.GET.get('pageNumber')
        else:
            page = PAGE_DEFAULT

        # Get Page Size
        if request.GET.get('pageSize'):
            numEntry = request.GET.get('pageSize')
            # IF Page size is 'ALL'
            if numEntry.lower() == 'all' or numEntry == -1:
                numEntry = numObject
        else:
            numEntry = NUM_ENTRY_DEFAULT

        querySetPaged = Paginator(querySet, int(numEntry))
        dataPaged = querySetPaged.get_page(page)
        dataSerialized = ReportSerializer(dataPaged, many=True)

        data = dict()
        data["total"] = numObject
        data['rows'] = dataSerialized.data
        return Response({'status': 0, 'object': data})


class APIGetReportByID(APIView):

    def get(self, request):
        if request.GET.get('id'):
            id = request.GET.get('id')
            try:
                id = int(id)
            except ValueError:
                return Response({'status': -1, 'message': "id is not integer"})
            try:
                report = ReportModel.objects.get(pk=id)
            except ReportModel.DoesNotExist:
                return Response({'status': -1, 'message': "Report is not existed"})
            dataSerialized = ReportSerializer(report, many=False)
            return Response({'status': 0, 'object': dataSerialized.data})


class APIAddReport(APIView):

    def post(self, request):
        reportForm = ReportForm(request.POST)
        if reportForm.is_valid():
            reportObj = reportForm.save(commit=False)
            reportObj.createBy = User.objects.get(pk=1)
            reportObj.status = ReportModel.STATE_REQUESTED
            reportObj.save()
            ProcessGenerateReportTask.delay(report=reportObj)
            dataSerialized = ReportSerializer(reportObj, many=False)
            return Response({'status': '0', 'object': dataSerialized.data})
        else:
            print(reportForm.errors)
            return Response({'status': '-1', 'message': 'Form is invalid', 'detail': reportForm.errors})


class APIDeleteReport(APIView):

    def post(self, request):
        reportID = request.POST.get('id', None)
        if reportID:
            try:
                report = ReportModel.objects.get(pk=reportID)
            except ReportModel.DoesNotExist:
                return Response({'status': -1, 'message': 'Report does not exist'})
            try:
                remove(report.fileReport.path)
            except OSError:
                pass
            name = report.name
            report.delete()
            return Response({'status': 0, 'message': "{} is successfully deleted".format(name)})
        return Response({'status': 1, 'message': " Report not found"})


class APIGetReportFile(APIView):

    def get(self, request):
        reportID = request.GET.get('id', None)
        print(reportID)
        if reportID:
            try:
                report = ReportModel.objects.get(pk=reportID)
            except ReportModel.DoesNotExist:
                return Response({'status': -1, 'message': 'Report does not exist'})
            reportFile = open(report.fileReport.path, 'rb')
            if report.format == ReportModel.FORMAT_PDF:
                response = HttpResponse(FileWrapper(reportFile), content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="{}"'.format(report.name + '.pdf')
                return response
            elif report.format == ReportModel.FORMAT_HTML:
                response = HttpResponse(FileWrapper(reportFile), content_type='text/html')
                response['Content-Disposition'] = 'attachment; filename="{}"'.format(report.name + '.html')
                return response
            elif report.format == ReportModel.FORMAT_XML:
                response = HttpResponse(FileWrapper(reportFile), content_type='text/xml')
                response['Content-Disposition'] = 'attachment; filename="{}"'.format(report.name + '.xml')
                return response
            elif report.format == ReportModel.FORMAT_XLS:
                response = HttpResponse(FileWrapper(reportFile), content_type='application/xls')
                response['Content-Disposition'] = 'attachment; filename="{}"'.format(report.name + '.xls')
                return response
        return Response({'status': 1, 'message': " Report not found"})