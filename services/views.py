from django.shortcuts import render
from django.views.generic import TemplateView
from dashboard.views import RenderSideBar
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.models import User
from .models import ServiceModel
from .serializers import ServiceSerializer
from .forms import ServiceForm, ServiceIDForm


PAGE_DEFAULT = 1
NUM_ENTRY_DEFAULT = 50


class ServicesView(TemplateView):
    template = 'services.html'

    def get(self, request, *args, **kwargs):
        form = ServiceForm()
        formEdit = ServiceForm(id='edit')
        sidebarHtml = RenderSideBar(request)
        context = {
            'sidebar': sidebarHtml,
            'form': form,
            'formEdit': formEdit,
        }
        return render(request, self.template, context)


class ServiceDetailView(TemplateView):
    template = 'service_detailed.html'

    def get(self, request, *args, **kwargs):
        print(kwargs['id'])
        form = ServiceForm()
        formEdit = ServiceForm(id='edit')
        sidebarHtml = RenderSideBar(request)
        context = {
            'sidebar': sidebarHtml,
            'form': form,
            'formEdit': formEdit,
        }
        return render(request, self.template, context)

#
# APIGetServices get services from these params:
#   searchText: Search content
#   sortName: Name of column is applied sort
#   sortOrder: sort entry by order 'asc' or 'desc'
#   pageSize: number of entry per page
#   pageNumber: page number of curent view


class APIGetServices(APIView):
    def get(self, request):
        numObject = ServiceModel.objects.all().count()

        # Filter by search keyword
        if request.GET.get('searchText'):
            search = request.GET.get('searchText')
            query = Q(name__icontains=search) | Q(port__icontains=search) | Q(description__icontains=search)
            querySet = ServiceModel.objects.filter(query)
        else:
            querySet = ServiceModel.objects.all()

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
        dataSerialized = ServiceSerializer(dataPaged, many=True)
        data = dict()
        data["total"] = numObject
        data['rows'] = dataSerialized.data
        return Response(data)


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
            dataSerialized = ServiceSerializer(retService, many=False)
            return Response(dataSerialized.data)
        else:
            return Response({'retVal': '-1'})


#
# APIAddService add new service
# return {'retVal': '-1'} if id not found
# return service object if it's success
#

class APIAddService(APIView):
    def post(self, request):
        serviceForm = ServiceForm(request.POST)
        if serviceForm.is_valid():
            entry = serviceForm.save(commit=False)
            entry.createBy = User.objects.get(pk=1)
            entry.save()
            dataSerialized = ServiceSerializer(entry, many=False)
            return Response(dataSerialized.data)
        else:
            retNotification = ''
            for field in serviceForm:
                for error in field.errors:
                    print(field)
                    retNotification += error
            for error in serviceForm.non_field_errors():
                retNotification += error
            retJson = {'notification': retNotification}
            return Response(retJson)


#
# APIDeleteService delete existing service
# return {'retVal': '-1'} if id not found
# return service object if it's success
#

class APIDeleteService(APIView):
    def post(self, request):
        serviceForm = ServiceIDForm(request.POST)
        if serviceForm.is_valid():
            successOnDelete = 0
            for rawID in serviceForm.data['id'].split(','):
                try:
                    id = int(rawID)
                except ValueError:
                    pass
                else:
                    try:
                        retService = ServiceModel.objects.get(pk=id)
                    except ServiceModel.DoesNotExist:
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

class APIUpdateService(APIView):
    def post(self, request):
        id = request.POST.get('id')
        serviceObj = ServiceModel.objects.get(pk=id)
        serviceForm = ServiceForm(request.POST, instance=serviceObj)
        if serviceForm.is_valid():
            entry = serviceForm.save()
            dataSerialized = ServiceSerializer(entry, many=False)
            return Response(dataSerialized.data)
        else:
            retNotification = ''
            for field in serviceForm:
                for error in field.errors:
                    retNotification += error
            for error in serviceForm.non_field_errors():
                retNotification += error
            retJson = {'notification': retNotification}
            return Response(retJson)