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
        if request.GET.get('search'):
            search = request.GET.get('search')
            query = Q(name__icontains=search) | Q(port__icontains=search) | Q(description__icontains=search)
            querySet = ServiceModel.objects.filter(query)
        else:
            querySet = ServiceModel.objects.all()
        if request.GET.get('page'):
            page = request.GET.get('page')
        else:
            page = PAGE_DEFAULT
        
        if request.GET.get('entry'):
            numEntry = request.GET.get('entry')
            if numEntry < 0:
                dataSerialized = ServiceSerializer(querySet, many=True)
                return Response(dataSerialized.data)
        else:
            numEntry = NUM_ENTRY_DEFAULT

        querySetPaged = Paginator(querySet, numEntry)
        dataPaged = querySetPaged.get_page(page)
        
        dataSerialized = ServiceSerializer(dataPaged, many=True)
        return Response(dataSerialized.data)

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