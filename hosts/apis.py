from django.utils.datastructures import MultiValueDictKeyError
from .models import HostModel
from .forms import HostForm, HostIDForm
from .serializers import HostSerializer, HostVulnSerializer, HostOSSerializer
from .ultil import GetHostsVuln, GetHosts, GetHostsCurrentVuln
from django.contrib.auth.models import User
from rest_framework.views import APIView
from django.core.paginator import Paginator
from django.db.models import Q
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required


PAGE_DEFAULT = 1
NUM_ENTRY_DEFAULT = 50


#   APIGetHostName get hostname  from id of hosts
#   Params: (id)
class APIGetHostName(APIView):

    @method_decorator(permission_required('hosts.view_hostmodel', raise_exception=True))
    def get(self, request):
        if request.GET.get('id'):
            try:
                id = int(request.GET.get('id'))
            except (ValueError, TypeError):
                return Response({'status': '-1', 'message': 'Value error',
                                 'detail': {"id": [{"message": "ID is not integer", "code": "value error"}]}})
            try:
                name = HostModel.objects.get(pk=id).hostName
            except HostModel.DoesNotExist:
                return Response({'status': '-1', 'message': 'Host does not exist'})
            return Response({'status': 0, 'object':name})
        else:
            return Response({'status': '-1', 'message': 'fields are required',
                             'detail': {"id": [{"message": "ID is required", "code": "required"}]}})


# APIGetHostsVuln get host and number of vulnerability [H, M, L, I]:
#   Params: (
#               Object Filter: [projectID], [scanID], [hostID], [vulnID], [serviceID],
#               Content Filter: [searchText], [sortOrder], [sortName], [pageSize], [pageNumber])
class APIGetHostsVuln(APIView):

    @method_decorator(permission_required('hosts.view_hostmodel', raise_exception=True))
    def get(self, request):
        kwarguments = dict()
        for kw in request.GET:
            kwarguments[kw] = request.GET.get(kw)

        retval = GetHostsVuln(**kwarguments)

        if retval['status'] != 0:
            return Response(retval)

        if request.GET.get('pageNumber'):
            try:
                page = int(request.GET.get('pageNumber'))
            except TypeError:
                page = PAGE_DEFAULT
        else:
            page = PAGE_DEFAULT

        # Get Page Size
        if request.GET.get('pageSize'):
            try:
                numEntry = int(request.GET.get('pageSize'))
            except TypeError:
                numEntry = NUM_ENTRY_DEFAULT
            # IF Page size is 'ALL'
            if str(numEntry).lower() == 'all' or numEntry == '-1':
                numEntry = retval['total']
        else:
            numEntry = NUM_ENTRY_DEFAULT
        querySetPaged = Paginator(retval['object'], numEntry)
        dataPaged = querySetPaged.get_page(page)
        dataSerialized = HostVulnSerializer(dataPaged, many=True)
        object = {
            'total': retval['total'],
            'rows': dataSerialized.data
        }
        return Response({'status': 0, 'object': object})


# APIGetHostsVuln get host and number of vulnerability [H, M, L, I]:
#   Params: (
#               Object Filter: [projectID], [scanID], [hostID], [vulnID], [serviceID],
#               Content Filter: [searchText], [sortOrder], [sortName], [pageSize], [pageNumber])
class APIGetHostsCurrentVuln(APIView):

    @method_decorator(permission_required('hosts.view_hostmodel', raise_exception=True))
    def get(self, request):
        kwarguments = dict()
        for kw in request.GET:
            kwarguments[kw] = request.GET.get(kw)
        retval = GetHostsCurrentVuln(**kwarguments)
        if retval['status'] != 0:
            return Response(retval)
        hosts = retval['object']

        # get total
        numObject = hosts.count()

        # Get Page Number
        if request.GET.get('pageNumber'):
            page = request.GET.get('pageNumber')
        else:
            page = PAGE_DEFAULT

        # Get Page Size
        if request.GET.get('pageSize'):
            numEntry = request.GET.get('pageSize')
            # IF Page size is 'ALL'
            if numEntry.lower() == 'all' or numEntry == '-1':
                numEntry = numObject
        else:
            numEntry = NUM_ENTRY_DEFAULT
        try:
            querySetPaged = Paginator(hosts, int(numEntry))
        except (ValueError, TypeError) as e:
            return Response({'status': -1, 'message': str(e)})
        dataPaged = querySetPaged.get_page(page)

        data = dict()
        data["total"] = numObject
        data['rows'] = dataPaged.object_list
        return Response({'status': 0, 'object': data})


# APIGetHosts get host from these params:
#   Params: (
#               Object Filter: [projectID], [scanID], [hostID], [vulnID], [serviceID],
#               Content Filter: [searchText], [sortOrder], [sortName], [pageSize], [pageNumber])
class APIGetHosts(APIView):

    @method_decorator(permission_required('hosts.view_hostmodel', raise_exception=True))
    def get(self, request):
        kwarguments = dict()
        for kw in request.GET:
            kwarguments[kw] = request.GET.get(kw)
        retval = GetHosts(**kwarguments)
        if retval['status'] != 0:
            return Response(retval)
        hosts = retval['object']

        # Filter by search keyword
        if request.GET.get('searchText'):
            search = request.GET.get('searchText')
            query = Q(ipAddr__icontains=search)\
                    | Q(hostName__icontains=search)\
                    | Q(osName__icontains=search) \
                    | Q(osVersion__icontains=search) \
                    | Q(description__icontains=search)
            hosts = hosts.filter(query)

        # get total
        numObject = hosts.count()
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
        querySet = hosts.order_by(sortString)

        # Get Page Number
        if request.GET.get('pageNumber'):
            page = request.GET.get('pageNumber')
        else:
            page = PAGE_DEFAULT

        # Get Page Size
        if request.GET.get('pageSize'):
            numEntry = request.GET.get('pageSize')
            # IF Page size is 'ALL'
            if numEntry.lower() == 'all' or numEntry == '-1':
                numEntry = numObject
        else:
            numEntry = NUM_ENTRY_DEFAULT
        try:
            querySetPaged = Paginator(querySet, int(numEntry))
        except (ValueError, TypeError) as e:
            return Response({'status':-1, 'message': str(e)})
        dataPaged = querySetPaged.get_page(page)
        dataSerialized = HostSerializer(dataPaged, many=True)
        data = dict()
        data["total"] = numObject
        data['rows'] = dataSerialized.data
        return Response({'status': 0, 'object': data})


#   APIGetHostsByID get host  from id of hosts
#   Params: (id)
class APIGetHostsByID(APIView):

    @method_decorator(permission_required('hosts.view_hostmodel', raise_exception=True))
    def get(self, request):
        if request.GET.get('id'):
            id = request.GET.get('id')
            try:
                retHost = HostModel.objects.get(pk=id)
            except (HostModel.DoesNotExist, ValueError):
                return Response({'status': '-1', 'message': 'Value error',
                                 'detail': {"id": [{"message": "ID is not integer", "code": "value error"}]}})
            dataSerialized = HostSerializer(retHost, many=False)
            return Response(dataSerialized.data)
        else:
            return Response({'status': '-1', 'message': 'fields are required',
                             'detail': {"id": [{"message": "ID is required", "code": "required"}]}})


# APIGetHostsOS get Operating System info from these params:
#   Params: (
#               Object Filter: [projectID], [scanID], [hostID], [vulnID], [serviceID],
#               Content Filter: [searchText], [sortOrder], [sortName], [pageSize], [pageNumber])
class APIGetHostsOS(APIView):

    @method_decorator(permission_required('hosts.view_hostmodel', raise_exception=True))
    def get(self, request):
        kwarguments = dict()
        for kw in request.GET:
            kwarguments[kw] = request.GET.get(kw)
        retval = GetHosts(**kwarguments)
        if retval['status'] != 0:
            return Response(retval)
        hosts = retval['object']

        # Filter by search keyword
        if request.GET.get('searchText'):
            search = request.GET.get('searchText')
            query = Q(ipAddr__icontains=search)\
                    | Q(hostName__icontains=search)\
                    | Q(osName__icontains=search) \
                    | Q(osVersion__icontains=search) \
                    | Q(description__icontains=search)
            hosts = hosts.filter(query)

        # get total
        numObject = hosts.count()
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
        querySet = hosts.order_by(sortString)

        # Get Page Number
        if request.GET.get('pageNumber'):
            page = request.GET.get('pageNumber')
        else:
            page = PAGE_DEFAULT

        # Get Page Size
        if request.GET.get('pageSize'):
            numEntry = request.GET.get('pageSize')
            # IF Page size is 'ALL'
            if numEntry.lower() == 'all' or numEntry == '-1':
                numEntry = numObject
        else:
            numEntry = NUM_ENTRY_DEFAULT
        try:
            querySetPaged = Paginator(querySet, int(numEntry))
        except (ValueError, TypeError) as e:
            return Response({'status': -1, 'message': str(e)})
        dataPaged = querySetPaged.get_page(page)
        dataSerialized = HostOSSerializer(dataPaged, many=True)
        data = dict()
        data["total"] = numObject
        data['rows'] = dataSerialized.data
        return Response({'status': 0, 'object': data})


# APIAddHost Add new Host to DB
class APIAddHost(APIView):

    @method_decorator(permission_required('hosts.add_hostmodel', raise_exception=True))
    def post(self, request):
        hostForm = HostForm(request.POST)
        if hostForm.is_valid():
            entry = hostForm.save(commit=False)
            entry.createBy = User.objects.get(username=request.user)
            entry.save()
            dataSerialized = HostSerializer(entry, many=False)
            return Response({'status': '0', 'object': dataSerialized.data})
        else:
            return Response({'status': '-1', 'message': 'Form is invalid', 'detail': hostForm.errors})


# APIAddHost delete Host in DB
class APIDeleteHost(APIView):

    @method_decorator(permission_required('hosts.delete_hostmodel', raise_exception=True))
    def post(self, request):
        hostForm = HostIDForm(request.POST)
        if hostForm.is_valid():
            successOnDelete = 0
            try:
                ids = hostForm.data['id'].split(',')
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
                        retService = HostModel.objects.get(pk=id)
                    except HostModel.DoesNotExist:
                        pass
                    else:
                        retService.delete()
                        successOnDelete = successOnDelete + 1
            if successOnDelete==1:
                return Response(
                    {'status': '0', 'message': '1 host is successfully deleted.', 'numDeleted': successOnDelete})
            else:
                return Response(
                            {'status': '0', 'message': '{} hosts are successfully deleted.'.format(successOnDelete), 'numDeleted': successOnDelete})
        else:
            return Response({'status': '-1', 'message': 'Form is invalid', 'detail': {hostForm.errors}})


# APIAddHost Update Host in DB
class APIUpdateHost(APIView):

    @method_decorator(permission_required('hosts.change_hostmodel', raise_exception=True))
    def post(self, request):
        if request.POST.get('id'):
            try:
                id = request.POST.get('id')
            except ValueError:
                return Response({'status': '-1', 'message': 'Value error',
                                 'detail': {"id": [{"message": "ID is not integer", "code": "value error"}]}})
            hostObj = HostModel.objects.get(pk=id)
            hostForm = HostForm(request.POST, instance=hostObj)
        else:
            return Response({'status': '-1', 'message': 'Fields are required',
                             'detail': {"id": [{"message": "ID is required", "code": "required"}]}})
        if hostForm.is_valid():
            entry = hostForm.save()
            dataSerialized = HostSerializer(entry, many=False)
            return Response({'status': '0', 'object': dataSerialized.data})
        else:
            return Response({'status': '-1', 'message': 'Form is invalid', 'detail': hostForm.errors})