from os import remove
from django.shortcuts import render
from django.views.generic import TemplateView
from dashboard.views import RenderSideBar
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.models import User
from services.models import ServiceModel
from scans.models import ScanTaskModel
from .models import SubmitModel
from django.contrib.auth.models import User
from .serializers import SubmitSerializer, SubmitNameSerializer
from .forms import SubmitAddForm, SubmitForm, SubmitIDForm
from .submitprocessor import ProcessFoundStoneZipXML, SubmitQueueElement, SUBMIT_OBJ_QUEUE
# from datetime import datetime, timedelta, time
# import dateutil.parser
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser

PAGE_DEFAULT = 1
NUM_ENTRY_DEFAULT = 50


class SubmitsView(TemplateView):
    template = 'submit/submit.html'

    def get(self, request, *args, **kwargs):
        form = SubmitAddForm()
        sidebarHtml = RenderSideBar(request)
        context = {
            'sidebar': sidebarHtml,
            'form': form,
        }
        return render(request, self.template, context)


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
        if request.GET.get('searchText'):
            search = request.GET.get('searchText')
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
        if request.GET.get('sortOrder') == 'asc':
            sortString = ''
        else:
            sortString = '-'

        # Get sort filed
        if request.GET.get('sortName'):
            sortString = sortString + request.GET.get('sortName')
        else:
            sortString = sortString + 'id'
        sortString = sortString.replace('.', '__')
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
            submitObj.status = 'uploaded'
            submitObj.save()
            submitQueueElement = SubmitQueueElement(submitObj=submitObj, overwrite=False)
            SUBMIT_OBJ_QUEUE.put(submitQueueElement)
            dataSerialized = SubmitSerializer(submitObj, many=False)
            return Response(dataSerialized.data)
        else:
            return Response(submitForm.errors.as_json())


#
# APIDeleteSubmit delete existing submit
# return {'retVal': '-1'} if id not found
# return {'retVal': 'Num of Success on Deleting'} if it's success
#

class APIDeleteSubmit(APIView):

    def post(self, request):
        print('aaa')
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
            return Response({'retVal': successOnDelete})
        else:
            return Response({'retVal': '-1'})
