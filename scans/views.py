from django.shortcuts import render
from django.views.generic import TemplateView
from dashboard.views import RenderSideBar
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.models import User
from .models import ScanTaskModel
# from .serializers import ServiceSerializer
from .forms import ScanForm


PAGE_DEFAULT = 1
NUM_ENTRY_DEFAULT = 50


class ScansView(TemplateView):
    template = 'scans.html'

    def get(self, request, *args, **kwargs):
        form = ScanForm()
        sidebarHtml = RenderSideBar(request)
        context = {
            'sidebar': sidebarHtml,
            'form': form,
        }
        return render(request, self.template, context)


class ServiceDetailView(TemplateView):
    def get(self, request, *args, **kwargs):
        pass

#
# APIGetServices get services from these params:
#   searchText: Search content
#   sortName: Name of column is applied sort
#   sortOrder: sort entry by order 'asc' or 'desc'
#   pageSize: number of entry per page
#   pageNumber: page number of curent view

#
# class APIGetServices(APIView):
#     def get(self, request):
#         numObject = ServiceModel.objects.all().count()
#
#         # Filter by search keyword
#         if request.GET.get('searchText'):
#             search = request.GET.get('searchText')
#             query = Q(name__icontains=search) | Q(port__icontains=search) | Q(description__icontains=search)
#             querySet = ServiceModel.objects.filter(query)
#         else:
#             querySet = ServiceModel.objects.all()
#
#         # Get sort order
#         if request.GET.get('sortOrder') == 'asc':
#             sortString = ''
#         else:
#             sortString = '-'
#
#         # Get sort filed
#         if request.GET.get('sortName'):
#             sortString = sortString + request.GET.get('sortName')
#         else:
#             sortString = sortString + 'id'
#         querySet = querySet.order_by(sortString)
#
#         # Get Page Number
#         if request.GET.get('pageNumber'):
#             page = request.GET.get('pageNumber')
#         else:
#             page = PAGE_DEFAULT
#
#         # Get Page Size
#         if request.GET.get('pageSize'):
#             numEntry = request.GET.get('pageSize')
#             # IF Page size is 'ALL'
#             if numEntry.lower() == 'all' or numEntry == -1:
#                 numEntry = numObject
#         else:
#             numEntry = NUM_ENTRY_DEFAULT
#         querySetPaged = Paginator(querySet, int(numEntry))
#         dataPaged = querySetPaged.get_page(page)
#         dataSerialized = ServiceSerializer(dataPaged, many=True)
#         data = dict()
#         data["total"] = numObject
#         data['rows'] = dataSerialized.data
#         return Response(data)
#
#
# #
# # APIGetServicesByID get services from id
# # return {'retVal': '-1'} if id not found
# # return service object if it's success
# #
#
# class APIGetServicesByID(APIView):
#     def get(self, request):
#         if request.GET.get('id'):
#             id = request.GET.get('id')
#             try:
#                 retService = ServiceModel.objects.get(pk=id)
#             except (ServiceModel.DoesNotExist, ValueError):
#                 return Response({'retVal': '-1'})
#             dataSerialized = ServiceSerializer(retService, many=False)
#             return Response(dataSerialized.data)
#         else:
#             return Response({'retVal': '-1'})
#
