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
from .models import VulnerabilityModel
from .serializers import VulnSerializer
from .forms import VulnForm, VulnIDForm


PAGE_DEFAULT = 1
NUM_ENTRY_DEFAULT = 50


class VulnerabilitiesView(TemplateView):
    template = 'vulns.html'

    def get(self, request, *args, **kwargs):
        form = VulnForm()
        formEdit = VulnForm(id='edit')
        sidebarHtml = RenderSideBar(request)
        context = {
            'sidebar': sidebarHtml,
            'form': form,
            'formEdit': formEdit,
        }
        return render(request, self.template, context)


class VulnerabilityDetailView(TemplateView):
    def get(self, request, *args, **kwargs):
        pass


#
# APIGetVulns get vulns from these params:
#   searchText: Search content
#   sortName: Name of column is applied sort
#   sortOrder: sort entry by order 'asc' or 'desc'
#   pageSize: number of entry per page
#   pageNumber: page number of curent view

class APIGetVulns(APIView):
    def get(self, request):
        numObject = VulnerabilityModel.objects.all().count()

        # Filter by search keyword
        if request.GET.get('searchText'):
            search = request.GET.get('searchText')

            # Query on Service Model
            queryServiceModel = Q(name__icontains=search)
            servicePK = ServiceModel.objects.filter(queryServiceModel).values_list('pk', flat=True)

            # Query on HostModel
            queryHostModel = Q(hostName__icontains=search)
            hostPK = HostModel.objects.filter(queryHostModel).values_list('pk', flat=True)

            # Query on ScanModel
            queryScanModel = Q(name__icontains=search)
            scanTaskPK = ScanTaskModel.objects.filter(queryScanModel).values_list('pk', flat=True)

            # Filter On Vuln
            queryVulnModel = Q(description__icontains=search)\
                             | Q(summary__icontains=search)\
                             | Q(levelRisk__icontains=search) \
                             | Q(service__in=servicePK) \
                             | Q(hostScanned__in=hostPK) \
                             | Q(scanTask__in=scanTaskPK)
            querySet = VulnerabilityModel.objects.filter(queryVulnModel)
        else:
            querySet = VulnerabilityModel.objects.all()

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
        dataSerialized = VulnSerializer(dataPaged, many=True)
        data = dict()
        data["total"] = numObject
        data['rows'] = dataSerialized.data
        return Response(data)


#
# APIGetVulnsByID get vulns from id
# return {'retVal': '-1'} if id not found
# return vuln object if it's success
#

class APIGetVulnsByID(APIView):
    def get(self, request):
        if request.GET.get('id'):
            id = request.GET.get('id')
            try:
                retService = VulnerabilityModel.objects.get(pk=id)
            except (VulnerabilityModel.DoesNotExist, ValueError):
                return Response({'retVal': '-1'})
            dataSerialized = VulnSerializer(retService, many=False)
            return Response(dataSerialized.data)
        else:
            return Response({'retVal': '-1'})

#
# APIGetServicesByID get services from id
# return {'retVal': '-1'} if id not found
# return service object if it's success
#

class APIGetServicesByID(APIView):
    def get(self, request):
        if request.GET.get('id'):
            id = request.GET.get('id')
            try:
                retService = ServiceModel.objects.get(pk=id)
            except (ServiceModel.DoesNotExist, ValueError):
                return Response({'retVal': '-1'})
            dataSerialized = VulnSerializer(retService, many=False)
            return Response(dataSerialized.data)
        else:
            return Response({'retVal': '-1'})


#
# APIAddVuln add new Vulnerability
# return {'retVal': '-1'} if id not found
# return Vuln object if it's success
#

class APIAddVuln(APIView):
    def post(self, request):
        vulnForm = VulnForm(request.POST)
        if vulnForm.is_valid():
            vulnObj = vulnForm.save(commit=True)
            dataSerialized = VulnSerializer(vulnObj, many=False)
            return Response(dataSerialized.data)
        else:
            retNotification = ''
            for field in vulnForm:
                for error in field.errors:
                    retNotification += error
            for error in vulnForm.non_field_errors():
                retNotification += error
            retJson = {'notification': retNotification}
            return Response(retJson)


#
# APIDeleteVuln delete existing vulnerability
# return {'retVal': '-1'} if id not found
# return {'retVal': 'Num of Success on Deleting'} if it's success
#

class APIDeleteVuln(APIView):
    def post(self, request):
        vulnForm = VulnIDForm(request.POST)
        if vulnForm.is_valid():
            successOnDelete = 0
            for rawID in vulnForm.data['id'].split(','):
                try:
                    id = int(rawID)
                except ValueError:
                    pass
                else:
                    try:
                        retVuln = VulnerabilityModel.objects.get(pk=id)
                    except ServiceModel.DoesNotExist:
                        pass
                    else:
                        retVuln.delete()
                        successOnDelete = successOnDelete + 1
            return Response({'retVal': successOnDelete})
        else:
            return Response({'retVal': '-1'})


#
# APIUpdateVuln update vulnerability
# return {'notification': 'error_msg'} if id not found
# return Vuln object if it's success
#

class APIUpdateVuln(APIView):
    def post(self, request):
        id = request.POST.get('id')
        vulnObj = VulnerabilityModel.objects.get(pk=id)
        vulnForm = VulnForm(request.POST)
        if vulnForm.is_valid():
            entry = vulnForm.save(instance=vulnObj)
            dataSerialized = VulnSerializer(entry, many=False)
            return Response(dataSerialized.data)
        else:
            retNotification = ''
            for field in vulnForm:
                for error in field.errors:
                    retNotification += error
            for error in vulnForm.non_field_errors():
                retNotification += error
            retJson = {'notification': retNotification}
            return Response(retJson)