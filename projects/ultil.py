from django.db.models import Q
from .serializers import *
import dateutil.parser


def GetProject(*args, **kwargs):
    querySet = ScanProjectModel.objects.all()

    searchText = kwargs.get('searchText', None)
    if searchText:
        if type(searchText) is list:
            try:
                search = searchText[0]
            except IndexError as e:
                return {'status': -1, 'message': str(e)}
        else:
            search = searchText
        query = Q(name__icontains=search) | \
                Q(dateCreated__icontains=search) | \
                Q(dateUpdate__icontains=search) | \
                Q(description__icontains=search)
        querySet = querySet.filter(query)

    fromDate = kwargs.get('fromDate', None)
    if fromDate:
        if type(fromDate) is list:
            try:
                fromDate = fromDate[0]
            except IndexError as e:
                return {'status': -1, 'message': str(e)}
        fromDate = dateutil.parser.parse(fromDate)
        querySet = querySet.filter(ScanProjectScanTask__startTime__gte=fromDate)

    toDate = kwargs.get('toDate', None)
    if toDate:
        if type(toDate) is list:
            try:
                toDate = toDate[0]
            except IndexError as e:
                return {'status': -1, 'message': str(e)}
            toDate = dateutil.parser.parse(toDate)
        querySet = querySet.filter(ScanProjectScanTask__startTime__lte=toDate)

    return {'status': 0, 'object': querySet}
