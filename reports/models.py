from django.db import models
from django.contrib.auth.models import User
from hosts.models import HostModel
from scans.models import ScanTaskModel
from projects.models import ScanProjectModel
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.deconstruct import deconstructible

FORMAT_REPORT = ['PDF', 'XML', 'XLS', 'HTML']
STATUS = ['uploaded', 'processing', 'processed', 'duplicated', 'error']


# @deconstructible
# class ValidateValueInArray(object):
#     def __init__(self, array):
#         self.array = array
#
#     def __call__(self, value):
#        if value not in self.array:
#            raise ValidationError(
#                gettext_lazy('%(value)s is not in defined format'),
#                params={'value': value},
#            )
#        else:
#            return value


class ReportModel(models.Model):
    """ Status of submitted files"""
    STATE_REQUESTED = 0
    STATE_PROCESSING = 1
    STATE_PROCESSED = 2
    STATE_ERROR = 3

    STATES = (
        (STATE_REQUESTED, "Requested"),
        (STATE_PROCESSING, "Processing"),
        (STATE_PROCESSED, "Processed"),
        (STATE_ERROR, "Error")
    )

    """ Mode of Report"""
    MODE_PROJECT = 0
    MODE_SCANTASK = 1
    MODE_HOST = 2
    MODE = (
        (MODE_PROJECT, "Project"),
        (MODE_SCANTASK, "ScanTask"),
        (MODE_HOST, "Host"),
    )
    """ Format of Report"""
    FORMAT_PDF = 0
    FORMAT_XML = 1
    FORMAT_XLS = 2
    FORMAT_HTML = 3
    FORMAT = (
        (FORMAT_PDF, 'PDF'),
        (FORMAT_XML, 'XML'),
        (FORMAT_XLS, 'XLS'),
        (FORMAT_HTML, 'HTML'),

    )

    name = models.CharField(verbose_name='Name of Report', max_length=64, unique=True)
    createBy = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    mode = models.SmallIntegerField(verbose_name="Mode of report", choices=MODE, default=MODE_HOST)
    fileReport = models.FileField(verbose_name='File report', blank=True, null=True)
    status = models.SmallIntegerField(verbose_name='Description of Vulnerability', choices=STATES,
                              default=STATE_REQUESTED, null=True, blank=True)
    # Format of File Report
    format = models.SmallIntegerField(verbose_name="File format of report", choices=FORMAT, default=FORMAT_PDF, null=True, blank=True)
    host = models.ForeignKey(HostModel, on_delete=models.SET_NULL, null=True, blank=True)
    scanTask = models.ForeignKey(ScanTaskModel, on_delete=models.SET_NULL, null=True, blank=True)
    scanProject = models.ForeignKey(ScanProjectModel, on_delete=models.SET_NULL, null=True, blank=True)

    # date Created and date Updated
    dateCreated = models.DateTimeField(auto_now_add=True)
    dateUpdate = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name