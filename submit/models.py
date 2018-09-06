from django.db import models
from scans.models import ScanTaskModel
from django.contrib.auth.models import User
from projects.models import ScanProjectModel


class SubmitModel(models.Model):
    fileSubmitted = models.FileField(verbose_name='File attachment', null=False, blank=False,
                                      upload_to='submits/%Y/%m/%d/',)
    description = models.CharField(verbose_name='Description of Vulnerability', max_length=1024, blank=True)
    project = models.ForeignKey(to=ScanProjectModel, on_delete=models.CASCADE)
    scanTask = models.ForeignKey(to=ScanTaskModel, on_delete=models.CASCADE, blank=True, null=True)
    submitter = models.ForeignKey(to=User, on_delete=models.CASCADE, blank=True)
    status = models.CharField(verbose_name='Description of Vulnerability', max_length=1024, default="Processing") # [uploaded, processed, duplicated, error]
    dateCreated = models.DateTimeField(auto_now_add=True)
    dateUpdated = models.DateTimeField(auto_now=True)
