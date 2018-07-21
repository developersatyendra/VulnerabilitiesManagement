from django.shortcuts import render
from django.views.generic import TemplateView
from dashboard.views import RenderSideBar
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.models import User
from services.models import ServiceModel
from hosts.models import HostModel
from scans.models import ScanTaskModel
from .models import SubmitModel
from .serializers import SubmitSerializer, SubmitNameSerializer
from .forms import SubmitAddForm, SubmitForm
# from datetime import datetime, timedelta, time
# import dateutil.parser
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser

PAGE_DEFAULT = 1
NUM_ENTRY_DEFAULT = 50


class SubmitsView(TemplateView):
    template = 'submit.html'

    def get(self, request, *args, **kwargs):
        form = SubmitAddForm()
        sidebarHtml = RenderSideBar(request)
        context = {
            'sidebar': sidebarHtml,
            'form': form,
        }
        return render(request, self.template, context)


# class VulnerabilityDetailView(TemplateView):
#     def get(self, request, *args, **kwargs):
#         pass


#
# APIGetVulns get vulns from these params:
#   searchText: Search content
#   sortName: Name of column is applied sort
#   sortOrder: sort entry by order 'asc' or 'desc'
#   pageSize: number of entry per page
#   pageNumber: page number of curent view

class APIGetSubmits(APIView):
    def get(self, request):
        numObject = SubmitModel.objects.all().count()

        # Filter by search keyword
        if request.GET.get('searchText'):
            search = request.GET.get('searchText')
            # Query on ScanModel
            queryScanModel = Q(name__icontains=search)
            scanTaskPK = ScanTaskModel.objects.filter(queryScanModel).values_list('pk', flat=True)

            # Filter On Vuln
            queryVulnModel = Q(description__icontains=search)\
                             | Q(fileSubmitted__icontains=search)\
                             | Q(dateCreated__icontains=search) \
                             | Q(scanTask__in=scanTaskPK)
            querySet = SubmitModel.objects.filter(queryVulnModel)
        else:
            querySet = SubmitModel.objects.all()

        # Get sort order
        if request.GET.get('sortOrder') == 'asc':
            sortString = ''
        else:
            sortString = '-'

        # Get sort filed
        if request.GET.get('sortName'):
            sortString = sortString + request.GET.get('sortName')
        else:
            sortString = sortString + 'id'
        querySet = querySet.order_by(sortString)
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
        dataSerialized = SubmitSerializer(dataPaged, many=True)
        data = dict()
        data["total"] = numObject
        data['rows'] = dataSerialized.data
        return Response(data)


#
# APIGetVulnsByID get vulns from id
# return {'retVal': '-1'} if id not found
# return vuln object if it's success
#

# class APIGetVulnByID(APIView):
#     def get(self, request):
#         if request.GET.get('id'):
#             id = request.GET.get('id')
#             try:
#                 retService = VulnerabilityModel.objects.get(pk=id)
#             except (VulnerabilityModel.DoesNotExist, ValueError):
#                 return Response({'retVal': '-1'})
#             dataSerialized = VulnSerializer(retService, many=False)
#             return Response(dataSerialized.data)
#         else:
#             return Response({'retVal': '-1'})

#
# APIStatVulns show number of vulns with datetime
# Param: starttime - Start time for statistic if this param is set to null
#        endtime - End time for statistic
# return {'retVal': '-1'} if syntax error
#

# class APIStatVulns(APIView):
#     def get(self, request):
#         print(request.GET)
#         if request.GET.get('starttime'):
#             try:
#                 starttime = dateutil.parser.parse(request.GET.get('starttime'))
#             except ValueError:
#                 return Response({'retVal': '-1'})
#         else:
#             return Response({'retVal': '-1'})
#
#         if request.GET.get('endtime'):
#             try:
#                 endtime = dateutil.parser.parse(request.GET.get('endtime'))
#             except ValueError:
#                 return Response({'retVal': '-1'})
#         else:
#             return Response({'retVal': '-1'})
#         days = []
#         low = []
#         med = []
#         high = []
#         for day in range(int((endtime - starttime).days)):
#             statDay= starttime + timedelta(day)
#             # Query Scan Task
#             queryScanModel = Q(startTime__gte = datetime.combine(statDay, time.min), startTime__lte=datetime.combine(statDay, time.max))
#             scanTaskPK = ScanTaskModel.objects.filter(queryScanModel).values_list('pk', flat=True)
#             if scanTaskPK:
#                 print(scanTaskPK)
#                 # Query vulns
#                 queryLowVuln = Q(scanTask__in=scanTaskPK, levelRisk=1)
#                 queryMedVuln = Q(scanTask__in=scanTaskPK, levelRisk=2)
#                 queryHiVuln = Q(scanTask__in=scanTaskPK, levelRisk=3)
#                 low.append(VulnerabilityModel.objects.filter(queryLowVuln).count())
#                 med.append(VulnerabilityModel.objects.filter(queryMedVuln).count())
#                 high.append(VulnerabilityModel.objects.filter(queryHiVuln).count())
#                 days.append(statDay)
#         return Response(
#             {
#                 'datetime': days,
#                 'low': low,
#                 'med': med,
#                 'high': high,
#             }
#         )


# APIAddSubmit add new Submit
# return {'retVal': '-1'} if id not found
# return Submit object if it's success
#

class APIAddSubmit(APIView):
    parser_classes = (MultiPartParser, FormParser, FileUploadParser,)
    def post(self, request):
        print(request.FILES)
        print(request.POST)
        submitForm = SubmitAddForm(request.POST, request.FILES)
        if submitForm.is_valid():
            submitObj = submitForm.save(commit=True)
            dataSerialized = SubmitSerializer(submitObj, many=False)
            return Response(dataSerialized.data)
        else:
            # retNotification = ''
            # for field in submitForm:
            #     for error in field.errors:
            #         print(field)
            #         retNotification += error
            # for error in submitForm.non_field_errors():
            #     retNotification += error
            # retJson = {'notification': retNotification}
            #
            return Response(submitForm.errors.as_json())


#
# APIDeleteVuln delete existing vulnerability
# return {'retVal': '-1'} if id not found
# return {'retVal': 'Num of Success on Deleting'} if it's success
#

# class APIDeleteVuln(APIView):
#     def post(self, request):
#         vulnForm = VulnIDForm(request.POST)
#         if vulnForm.is_valid():
#             successOnDelete = 0
#             for rawID in vulnForm.data['id'].split(','):
#                 try:
#                     id = int(rawID)
#                 except ValueError:
#                     pass
#                 else:
#                     try:
#                         retVuln = VulnerabilityModel.objects.get(pk=id)
#                     except ServiceModel.DoesNotExist:
#                         pass
#                     else:
#                         retVuln.delete()
#                         successOnDelete = successOnDelete + 1
#             return Response({'retVal': successOnDelete})
#         else:
#             return Response({'retVal': '-1'})


#
# APIUpdateVuln update vulnerability
# return {'notification': 'error_msg'} if id not found
# return Vuln object if it's success
#

# class APIUpdateVuln(APIView):
#     def post(self, request):
#         id = request.POST.get('id')
#         vulnObj = VulnerabilityModel.objects.get(pk=id)
#         vulnForm = VulnForm(request.POST)
#         if vulnForm.is_valid():
#             entry = vulnForm.save(instance=vulnObj)
#             dataSerialized = VulnSerializer(entry, many=False)
#             return Response(dataSerialized.data)
#         else:
#             retNotification = ''
#             for field in vulnForm:
#                 for error in field.errors:
#                     retNotification += error
#             for error in vulnForm.non_field_errors():
#                 retNotification += error
#             retJson = {'notification': retNotification}
#             return Response(retJson)