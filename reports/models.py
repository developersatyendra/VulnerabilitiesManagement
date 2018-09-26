from django.db import models
from django.contrib.auth.models import User
from hosts.models import HostModel
from scans.models import ScanTaskModel
from projects.models import ScanProjectModel
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy
from django.core.validators import MaxValueValidator, MinValueValidator

FORMAT_REPORT = ['PDF', 'XML', 'XLS', 'HTML']


def ValidateFormatReport(value):
    if value not in FORMAT_REPORT:
        raise ValidationError(
            gettext_lazy('%(value)s is not in defined format report'),
            params={'value': value},
        )


class ReportModel(models.Model):
    name = models.CharField(verbose_name='Name of Report', max_length=64, unique=True)
    createBy = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    mode = models.IntegerField(verbose_name="Mode of report: 0 -Project, 1 -ScanTask, 2 -Host",
                               validators=[MaxValueValidator(2), MinValueValidator(0)])
    fileReport = models.FileField(verbose_name='File report', blank=True, null=True)

    # Format of File Report
    format = models.CharField(verbose_name="File format of report", validators=[ValidateFormatReport], max_length=64)
    host = models.ForeignKey(HostModel, on_delete=models.SET_NULL, null=True, blank=True)
    scanTask = models.ForeignKey(ScanTaskModel, on_delete=models.SET_NULL, null=True, blank=True)
    scanProject = models.ForeignKey(ScanProjectModel, on_delete=models.SET_NULL, null=True, blank=True)
    # date Created and date Updated
    dateCreated = models.DateTimeField(auto_created=True)
    dateUpdate = models.DateTimeField(auto_now=True)