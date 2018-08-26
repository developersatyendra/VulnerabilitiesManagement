from django.shortcuts import render
from django.views.generic import TemplateView
from dashboard.views import RenderSideBar
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.models import User
from .models import ScanProjectModel
from .serializers import ProjectSerializer
from .forms import ProjectForm,ProjectIDForm


PAGE_DEFAULT = 1
NUM_ENTRY_DEFAULT = 50


class ProjectsView(TemplateView):
    template = 'projects.html'

    def get(self, request, *args, **kwargs):
        form = ProjectForm()
        formEdit = ProjectForm(id='edit')
        sidebarHtml = RenderSideBar(request)
        context = {
            'sidebar': sidebarHtml,
            'form': form,
            'formEdit': formEdit,
        }
        return render(request, self.template, context)


class ProjectsDetailView(TemplateView):
    template = 'project_detailed.html'

    def get(self, request, *args, **kwargs):
        form = ProjectForm()
        sidebarHtml = RenderSideBar(request)
        context = {
            'sidebar': sidebarHtml,
            'form': form,
        }
        return render(request, self.template, context)


######################################################
#   APIGetProjects get Projects from these params:
#   searchText: Search content
#   sortName: Name of column is applied sort
#   sortOrder: sort entry by order 'asc' or 'desc'
#   pageSize: number of entry per page
#   pageNumber: page number of curent view


class APIGetProjects(APIView):
    def get(self, request):
        numObject = ScanProjectModel.objects.all().count()

        # Filter by search keyword
        if request.GET.get('searchText'):
            search = request.GET.get('searchText')
            # Query on Projects Model
            query = Q(name__icontains=search) |\
                    Q(createDate__icontains=search) | \
                    Q(updateDate__icontains=search) | \
                    Q(description__icontains=search)
            querySet = ScanProjectModel.objects.filter(query)
        else:
            querySet = ScanProjectModel.objects.all()

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
        dataSerialized = ProjectSerializer(dataPaged, many=True)
        data = dict()
        data["total"] = numObject
        data['rows'] = dataSerialized.data
        return Response({'status':0, 'object':data})

######################################################
# APIGetProjectByID get project from id
# return {'status': '-1'} if something wrong
# return project object if it's success
#

class APIGetProjectByID(APIView):
    def get(self, request):
        if request.GET.get('id'):
            id = request.GET.get('id')
            try:
                retService = ScanProjectModel.objects.get(pk=id)
            except ValueError:
                return Response({'status': '-1', 'message': 'Value error',
                                 'detail': {"id": [{"message": "ID is not integer", "code": "value error"}]}})
            except ScanProjectModel.DoesNotExist:
                return Response({'status': '-1', 'message': 'Project ID does not exist',
                                 'detail': {}})
            dataSerialized = ProjectSerializer(retService, many=False)
            return Response({'status': '0', 'object': dataSerialized.data})
        else:
            return Response({'status': '-1', 'message': 'fields are required',
                             'detail': {"id": [{"message": "ID is required", "code": "required"}]}})

######################################################
# APIAddProject add new project
# return {'status': '-1'} if id not found
# return Vuln object if it's success
#

class APIAddProject(APIView):
    def post(self, request):
        print(request.POST)
        projectForm = ProjectForm(request.POST)
        if projectForm.is_valid():
            vulnObj = projectForm.save(commit=False)
            vulnObj.createBy = User.objects.get(pk=1)
            vulnObj.save()
            dataSerialized = ProjectSerializer(vulnObj, many=False)
            return Response({'status': '0', 'object': dataSerialized.data})
        else:
            return Response({'status': '-1', 'message': 'Form is invalid', 'detail': projectForm.errors})


######################################################
# APIDeleteProjects delete existing projects
# return {'retVal': '-1'} if id not found
# return {'retVal': 'Num of Success on Deleting'} if it's success
#

class APIDeleteProject(APIView):
    def post(self, request):
        projectForm = ProjectIDForm(request.POST)
        if projectForm.is_valid():
            successOnDelete = 0
            try:
                ids = projectForm.data['id'].split(',')
            except MultiValueDictKeyError:
                return Response({'status': '-1', 'message': 'Fields are required',
                                 'detail': {"id": [{"message": "ID is required", "code": "required"}]}})
            for rawID in ids:
                try:
                    id = int(rawID)
                except ValueError:
                    pass
                else:
                    try:
                        retVuln = ScanProjectModel.objects.get(pk=id)
                    except ScanProjectModel.DoesNotExist:
                        pass
                    else:
                        retVuln.delete()
                        successOnDelete = successOnDelete + 1
            if successOnDelete==1:
                return Response(
                    {'status': '0', 'message': '1 Project is successfully deleted.', 'numDeleted':successOnDelete})
            else:
                return Response(
                {'status': '0', 'message': '{} Projects are successfully deleted.'.format(successOnDelete), 'numDeleted':successOnDelete})
        else:
            return Response({'status': '-1', 'message': 'Form is invalid', 'detail': {projectForm.errors}})


######################################################
# APIUpdateProject update project
# return {'notification': 'error_msg'} if id not found
# return Project object if it's success
#

class APIUpdateProject(APIView):
    def post(self, request):
        if request.POST.get('id'):
            try:
                id = int(request.POST.get('id'))
            except ValueError:
                return Response({'status': '-1', 'message': 'Value error',
                                 'detail': {"id": [{"message": "ID is not integer", "code": "value error"}]}})
            projectObj = ScanProjectModel.objects.get(pk=id)
            projectForm = ProjectForm(request.POST, instance=projectObj)
        else:
            return Response({'status': '-1', 'message': 'Fields are required',
                             'detail': {"id": [{"message": "ID is required", "code": "required"}]}})
        if projectForm.is_valid():
            entry = projectForm.save()
            dataSerialized = ProjectSerializer(entry, many=False)
            return Response({'status': '0', 'object': dataSerialized.data})
        else:
            return Response({'status': '-1', 'message': 'Form is invalid', 'detail': projectForm.errors})