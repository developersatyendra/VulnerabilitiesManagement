from django.shortcuts import render
from django.views.generic import TemplateView
from dashboard.views import RenderSideBar
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.models import User
from .models import ScanTaskModel
from .serializers import ScanSerializer
from .forms import ScanForm, ScanIDForm
from projects.models import ScanProjectModel
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser


PAGE_DEFAULT = 1
NUM_ENTRY_DEFAULT = 50


class ScansView(TemplateView):
    template = 'scans.html'

    def get(self, request, *args, **kwargs):
        form = ScanForm()
        formEdit = ScanForm(id='edit')
        sidebarHtml = RenderSideBar(request)
        context = {
            'sidebar': sidebarHtml,
            'form': form,
            'formEdit': formEdit,
        }
        return render(request, self.template, context)


class ScansDetailView(TemplateView):
    def get(self, request, *args, **kwargs):
        pass

#
#   APIGetScans get services from these params:
#   searchText: Search content
#   sortName: Name of column is applied sort
#   sortOrder: sort entry by order 'asc' or 'desc'
#   pageSize: number of entry per page
#   pageNumber: page number of curent view
#

class APIGetScans(APIView):
    def get(self, request):
        numObject = ScanTaskModel.objects.all().count()

        # Filter by search keyword
        if request.GET.get('searchText'):
            search = request.GET.get('searchText')
            # Query on Projects Model
            queryProjectModel = Q(name__icontains=search)
            projectPK = ScanProjectModel.objects.filter(queryProjectModel).values_list('pk', flat=True)

            # Query on ScanTask
            query = Q(name__icontains=search) |\
                    Q(startTime__icontains=search) | \
                    Q(endTime__icontains=search) | \
                    Q(scanProject__in=projectPK) | \
                    Q(description__icontains=search)
            querySet = ScanTaskModel.objects.filter(query)
        else:
            querySet = ScanTaskModel.objects.all()

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
        dataSerialized = ScanSerializer(dataPaged, many=True)
        data = dict()
        data["total"] = numObject
        data['rows'] = dataSerialized.data
        return Response(data)


# #
# # APIGetScanByID get services from id
# # return {'retVal': '-1'} if id not found
# # return service object if it's success
# #

class APIGetScanByID(APIView):
    def get(self, request):
        if request.GET.get('id'):
            id = request.GET.get('id')
            try:
                retService = ScanTaskModel.objects.get(pk=id)
            except (ScanTaskModel.DoesNotExist, ValueError):
                return Response({'retVal': '-1'})
            dataSerialized = ScanSerializer(retService, many=False)
            return Response(dataSerialized.data)
        else:
            return Response({'retVal': '-1'})
#
# APIAddScan add new Vulnerability
# return {'retVal': '-1'} if id not found
# return Vuln object if it's success
#


class APIAddScan(APIView):
    parser_classes = (MultiPartParser, FormParser, FileUploadParser,)

    def post(self, request, format=None):
        for upload in request.FILES:
            print(upload)
        scanForm = ScanForm(request.POST, request.FILES)
        if scanForm.is_valid():
            scanObj = scanForm.save(commit=False)
            scanObj.scanBy = User.objects.get(pk=1)
            scanObj.submitter = User.objects.get(pk=1)
            # scanObj.fileAttachment = request.FILES['fileAttachment']
            scanObj.save()
            dataSerialized = ScanSerializer(scanObj, many=False)
            return Response(dataSerialized.data)
        else:
            retNotification = ''
            for field in scanForm:
                for error in field.errors:
                    retNotification += error
                    print(field)
            for error in scanForm.non_field_errors():
                retNotification += error
            retJson = {'notification': retNotification}
            return Response(retJson)


#
# APIDeleteScan delete existing Scan Tasks
# return {'retVal': '-1'} if id not found
# return {'retVal': 'Num of Success on Deleting'} if it's success
#

class APIDeleteScan(APIView):
    def post(self, request):
        scanForm = ScanIDForm(request.POST)
        if scanForm.is_valid():
            successOnDelete = 0
            for rawID in scanForm.data['id'].split(','):
                try:
                    id = int(rawID)
                except ValueError:
                    pass
                else:
                    try:
                        retVuln = ScanTaskModel.objects.get(pk=id)
                    except ScanTaskModel.DoesNotExist:
                        pass
                    else:
                        retVuln.delete()
                        successOnDelete = successOnDelete + 1
            return Response({'retVal': successOnDelete})
        else:
            return Response({'retVal': '-1'})


#
# APIUpdateScan update Scan Tasks
# return {'notification': 'error_msg'} if id not found
# return Scan object if it's success
#

class APIUpdateScan(APIView):
    def post(self, request):
        id = request.POST.get('id')
        scanObj = ScanTaskModel.objects.get(pk=id)
        scanForm = ScanForm(request.POST, instance=scanObj)
        if scanForm.is_valid():
            entry = scanForm.save()
            dataSerialized = ScanSerializer(entry, many=False)
            return Response(dataSerialized.data)
        else:
            retNotification = ''
            for field in scanForm:
                for error in field.errors:
                    retNotification += error
            for error in scanForm.non_field_errors():
                retNotification += error
            retJson = {'notification': retNotification}
            return Response(retJson)
