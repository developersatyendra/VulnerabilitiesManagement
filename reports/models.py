from django.db import models
from django.contrib.auth.models import User
from scans.models import ScanTaskModel
from projects.models import ScanProjectModel


class ReportModel(models.Model):
    createBy = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(verbose_name='Name of Report', max_length=64)
    file = models.FileField(verbose_name='File report')
    scanTask = models.ForeignKey(ScanTaskModel, on_delete=models.SET_NULL, null=True)
    scanProject = models.ForeignKey(ScanProjectModel, on_delete=models.SET_NULL, null=True)
    dateCreated = models.DateTimeField(auto_created=True)
    dateUpdate = models.DateTimeField(auto_now=True)