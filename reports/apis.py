from rest_framework.views import APIView
from .models import ReportModel
from .forms import ReportForm
from .serializers import ReportSerializer
from django.contrib.auth.models import User
from rest_framework.response import Response
from os import remove


class CreateReportAPI(APIView):

    def post(self, request):
        reportForm = ReportForm(request.POST)
        if reportForm.is_valid():
            reportObj = reportForm.save(commit=False)
            reportObj.createBy = User.objects.get(pk=1)
            reportObj.save()
            dataSerialized = ReportSerializer(reportObj, many=False)
            return Response({'status': '0', 'object': dataSerialized.data})
        else:
            return Response({'status': '-1', 'message': 'Form is invalid', 'detail': reportForm.errors})


class DeleteReportAPI(APIView):

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