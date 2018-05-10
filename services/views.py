from django.shortcuts import render
from django.views.generic import TemplateView
from dashboard.views import RenderSideBar
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ServiceModel
from .serializers import ServiceSerializer
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from .forms import ServiceForm
from django.contrib.auth.models import User
import json

PAGE_DEFAULT = 1
NUM_ENTRY_DEFAULT = 50


class ServicesView(TemplateView):
    template = 'services.html'

    def get(self, request, *args, **kwargs):
        form = ServiceForm()
        serviceObjects = ServiceModel.objects.all()[:1000]
        sidebarHtml = RenderSideBar(request)
        context = {
            'sidebar': sidebarHtml,
            'ServiceData': serviceObjects,
            'form': form,
        }
        return render(request, self.template, context)


class ServiceDetailView(TemplateView):
    def get(self, request, *args, **kwargs):
        pass


class APIGetServices(APIView):
    def get(self, request):
        numObject = ServiceModel.objects.all().count()

        # Filter by search keyword
        if request.GET.get('searchText'):
            search = request.GET.get('searchText')
            query = Q(name__icontains=search) | Q(port__icontains=search) | Q(description__icontains=search)
            querySet = ServiceModel.objects.all().filter(query)
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
        data = {}
        data["total"] = numObject
        data['rows'] = dataSerialized.data
        return Response(data)

    def put(self, request):
        pass


class APIGetServicesByID(APIView):
    def get(self, request):
        if request.GET.get('id'):
            id = request.GET.get('id')
            try:
                retService = ServiceModel.objects.get(pk=id)
            except ServiceModel.DoesNotExist:
                return JsonResponse({'retVal': '-1'})
            dataSerialized = ServiceSerializer(retService, many=False)
            return Response(dataSerialized.data)
        else:
            return JsonResponse({'retVal': '-1'})

    def put(self, request):
        pass


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
                    retNotification += error
            for error in serviceForm.non_field_errors():
                retNotification += error
            retJson = {'notification': retNotification}
            return JsonResponse(retJson)

    def put(self, request):
        pass



class APIDeleteService(APIView):
    def get(self, request):
        if request.GET.get('id'):
            id = request.GET.get('id')
            try:
                retService = ServiceModel.objects.get(pk=id)
            except ServiceModel.DoesNotExist:
                return JsonResponse({'retVal': '-1'})
            retService.delete()
            return JsonResponse({'retVal': '0'})
        else:
            return JsonResponse({'retVal': '-1'})

    def post(self, request):
        print("Test---------------------")
        for key in request.POST:
            print(key)
            value = request.POST[key]
            print(value)

        # if data is raw from ajax post
        ids = []
        if request.is_ajax():
            if request.method == 'POST':
                print('Raw Data: {}'.format(request.body))
                dataDeserialized = json.loads(request.body)
                for service in dataDeserialized:
                    ids.append(service["id"])

        # if data post is object
        elif request.POST.get('ids'):
            ids = request.POST.get('ids')
        else:
            return Response({'retVal': '-1'})

        successOnDelete = 0
        for id in ids:
            try:
                retService = ServiceModel.objects.get(pk=id)
            except ServiceModel.DoesNotExist:
                pass
            else:
                retService.delete()
                successOnDelete = successOnDelete + 1
        return Response({'retVal': successOnDelete})

    def put(self, request):
        pass


class APIUpdateService(APIView):
    def get(self, request):
        if request.GET.get('id'):
            id = request.GET.get('id')
            try:
                retService = ServiceModel.objects.get(pk=id)
            except ServiceModel.DoesNotExist:
                return JsonResponse({'retVal': '-1'})
            if request.GET.get('name'):
                retService.name = request.GET.get('name')
            if request.GET.get('port'):
                retService.port = request.GET.get('port')
            if request.GET.get('description'):
                retService.description = request.GET.get('description')
            retService.save()
            dataSerialized = ServiceSerializer(retService, many=False)
            return Response(dataSerialized.data)
        else:
            return JsonResponse({'retVal': '-1'})

    def put(self, request):
        pass