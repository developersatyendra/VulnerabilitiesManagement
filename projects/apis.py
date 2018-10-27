from django.utils.datastructures import MultiValueDictKeyError
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.contrib.auth.models import User
from .serializers import *
from .forms import ProjectForm, ProjectIDForm
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required
from django.conf import settings
from .ultil import *

PAGE_DEFAULT = 1
NUM_ENTRY_DEFAULT = 50
# High is >= LEVEL_HIGH
LEVEL_HIGH = getattr(settings, 'LEVEL_HIGH')

# Med is >= LEVEL_MED AND < LEVEL_HIGH
LEVEL_MED = getattr(settings, 'LEVEL_MED')

# Low is > LEVEL_INFO AND < LEVEL_MED
# Info is = LEVEL_INFO
LEVEL_INFO = getattr(settings, 'LEVEL_INFO')

######################################################
#   APIGetProjectName get Name of Project from id
#

class APIGetProjectName(APIView):

    @method_decorator(permission_required('projects.view_scanprojectmodel', raise_exception=True))
    def get(self, request):
        try:
            id = int(request.GET.get('id'))
        except (ValueError, TypeError):
            return Response({'status': '-1', 'message': 'Value error',
                             'detail': {"id": [{"message": "ID is not integer", "code": "value error"}]}})
        try:
            name = ScanProjectModel.objects.get(pk=id).name
        except ScanProjectModel.DoesNotExist:
            return Response({'status': '-1', 'message': 'Project does not exist'})
        return Response({'status': 0, 'object':name})


######################################################
#   APIGetProjects get Projects from these params:
#   searchText: Search content
#   sortName: Name of column is applied sort
#   sortOrder: sort entry by order 'asc' or 'desc'
#   pageSize: number of entry per page
#   pageNumber: page number of curent view


class APIGetProjects(APIView):

    @method_decorator(permission_required('projects.view_scanprojectmodel', raise_exception=True))
    def get(self, request):
        retval = GetProject(**request.GET)
        if retval['status'] !=0:
            return  Response({'status': retval['status'], 'message': retval['message']})
        querySet = retval['object']

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
        return Response({'status': 0, 'object': data})


######################################################
# APIGetProjectByID get project from id
# return {'status': '-1'} if something wrong
# return project object if it's success
#

class APIGetProjectByID(APIView):

    @method_decorator(permission_required('projects.view_scanprojectmodel', raise_exception=True))
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
# APIGetProjectVuln get projects's vulns
#

class APIGetProjectVulns(APIView):

    @method_decorator(permission_required('projects.view_scanprojectmodel', raise_exception=True))
    def get(self, request):
        retval = GetProject(**request.GET)
        if retval['status'] !=0:
            return Response({'status': retval['status'], 'message': retval['message']})
        projects = retval['object']
        projects = projects.annotate(
            high=Count('ScanProjectScanTask__ScanInfoScanTask__vulnFound', filter=Q(ScanProjectScanTask__ScanInfoScanTask__vulnFound__levelRisk__gte=LEVEL_HIGH)),
            med=Count('ScanProjectScanTask__ScanInfoScanTask__vulnFound', filter=(Q(ScanProjectScanTask__ScanInfoScanTask__vulnFound__levelRisk__gte=LEVEL_MED) & Q(
                ScanProjectScanTask__ScanInfoScanTask__vulnFound__levelRisk__lt=LEVEL_HIGH))),
            low=Count('ScanProjectScanTask__ScanInfoScanTask__vulnFound', filter=Q(ScanProjectScanTask__ScanInfoScanTask__vulnFound__levelRisk__gt=LEVEL_INFO) & Q(
                ScanProjectScanTask__ScanInfoScanTask__vulnFound__levelRisk__lt=LEVEL_MED)),
            info=Count('ScanProjectScanTask__ScanInfoScanTask__vulnFound', filter=Q(ScanProjectScanTask__ScanInfoScanTask__vulnFound__levelRisk=LEVEL_INFO)),
            numScanTasks=Count('ScanProjectScanTask', distinct=True),
        )
        dataSerialized = ProjectVulnSerializer(projects, many=True)
        return Response({'status': '0', 'object': dataSerialized.data})

######################################################
# APIAddProject add new project
# return {'status': '-1'} if id not found
# return Vuln object if it's success
#

class APIAddProject(APIView):

    @method_decorator(permission_required('projects.add_scanprojectmodel', raise_exception=True))
    def post(self, request):
        projectForm = ProjectForm(request.POST)
        if projectForm.is_valid():
            vulnObj = projectForm.save(commit=False)
            vulnObj.createBy = User.objects.get(username=request.user)
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

    @method_decorator(permission_required('projects.delete_scanprojectmodel', raise_exception=True))
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

    @method_decorator(permission_required('projects.change_scanprojectmodel', raise_exception=True))
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
