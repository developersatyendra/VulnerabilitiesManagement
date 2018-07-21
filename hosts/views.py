from django.shortcuts import render
from django.views.generic import TemplateView
from dashboard.views import RenderSideBar
from .models import HostModel
from .forms import HostForm, HostIDForm
from .serializers import HostSerializer
from django.contrib.auth.models import User
from rest_framework.views import APIView
from django.core.paginator import Paginator
from django.db.models import Q
from rest_framework.response import Response

PAGE_DEFAULT = 1
NUM_ENTRY_DEFAULT = 50


class HostsView(TemplateView):
    template = 'hosts.html'

    def get(self, request, *args, **kwargs):
        form = HostForm()
        formEdit = HostForm(id='edit')
        # serviceObjects = HostModel.objects.all()[:1000]
        sidebarHtml = RenderSideBar(request)
        context = {
            'sidebar': sidebarHtml,
            # 'ServiceData': serviceObjects,
            'form': form,
            'formEdit': formEdit,
        }
        return render(request, self.template, context)


class HostDetailView(TemplateView):
    def get(self, request, *args, **kwargs):
        pass


#
# APIGetHosts get host from these params:
#   searchText: Search content
#   sortName: Name of column is applied sort
#   sortOrder: sort entry by order 'asc' or 'desc'
#   pageSize: number of entry per page
#   pageNumber: page number of current view
#

class APIGetHosts(APIView):
    def get(self, request):
        numObject = HostModel.objects.all().count()

        # Filter by search keyword
        if request.GET.get('searchText'):
            search = request.GET.get('searchText')
            query = Q(ipAdr__icontains=search)\
                    | Q(hostName__icontains=search)\
                    | Q(platform__icontains=search) \
                    | Q(osName__icontains=search) \
                    | Q(osVersion__icontains=search) \
                    | Q(description__icontains=search)
            querySet = HostModel.objects.filter(query)
        else:
            querySet = HostModel.objects.all()

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
        dataSerialized = HostSerializer(dataPaged, many=True)
        data = dict()
        data["total"] = numObject
        data['rows'] = dataSerialized.data
        return Response(data)


#
# APIGetHostsByID get hosts from ids
# return {'retVal': '-1'} if id not found
# return service object if it's success
#

class APIGetHostsByID(APIView):
    def get(self, request):
        if request.GET.get('id'):
            id = request.GET.get('id')
            try:
                retService = HostModel.objects.get(pk=id)
            except (HostModel.DoesNotExist, ValueError):
                return Response({'retVal': '-1'})
            dataSerialized = HostSerializer(retService, many=False)
            return Response(dataSerialized.data)
        else:
            return Response({'retVal': '-1'})


#
# APIAddHost add new Host
# return {'retVal': '-1'} if id not found
# return service object if it's success
#

class APIAddHost(APIView):
    def post(self, request):
        hostForm = HostForm(request.POST)
        if hostForm.is_valid():
            entry = hostForm.save(commit=False)
            entry.createBy = User.objects.get(pk=1)
            entry.save()
            dataSerialized = HostSerializer(entry, many=False)
            return Response(dataSerialized.data)
        else:
            retNotification = ''
            for field in hostForm:
                for error in field.errors:
                    retNotification += error
            for error in hostForm.non_field_errors():
                retNotification += error
            retJson = {'notification': retNotification}
            return Response(retJson)


#
# APIDeleteHost delete existing Host
# return {'retVal': '-1'} if id not found
# return number of Host object deleted if it's success
#

class APIDeleteHost(APIView):
    def post(self, request):
        hostForm = HostIDForm(request.POST)
        if hostForm.is_valid():
            successOnDelete = 0
            for rawID in hostForm.data['id'].split(','):
                try:
                    id = int(rawID)
                except ValueError:
                    pass
                else:
                    try:
                        retService = HostModel.objects.get(pk=id)
                    except HostModel.DoesNotExist:
                        pass
                    else:
                        retService.delete()
                        successOnDelete = successOnDelete + 1
            return Response({'retVal': successOnDelete})
        else:
            return Response({'retVal': '-1'})


#
# APIUpdateService delete existing service
# return {'notification': 'error_msg'} if id not found
# return service object if it's success
#

class APIUpdateHost(APIView):
    def post(self, request):
        id = request.POST.get('id')
        hostObj = HostModel.objects.get(pk=id)
        hostForm = HostForm(request.POST, instance=hostObj)
        if hostForm.is_valid():
            entry = hostForm.save()
            dataSerialized = HostSerializer(entry, many=False)
            return Response(dataSerialized.data)
        else:
            retNotification = ''
            for field in hostForm:
                for error in field.errors:
                    retNotification += error
            for error in hostForm.non_field_errors():
                retNotification += error
            retJson = {'notification': retNotification}
            return Response(retJson)