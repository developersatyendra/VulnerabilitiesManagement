from django.db import models
from scans.models import ScanTaskModel
from django.contrib.auth.models import User


class SubmitModel(models.Model):
    fileSubmitted = models.FileField(verbose_name='File attachment', null=False, blank=False,
                                      upload_to='submits/%Y/%m/%d/',)
    description = models.CharField(verbose_name='Description of Vulnerability', max_length=1024, blank=True)
    scanTask = models.ForeignKey(to=ScanTaskModel, on_delete=models.CASCADE, null=True, blank=True)
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(verbose_name='Description of Vulnerability', max_length=1024, default="Processing")
    dateCreated = models.DateTimeField(auto_now_add=True)
    dateUpdated = models.DateTimeField(auto_now=True)
