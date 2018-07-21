from django.db import models
from scans.models import ScanTaskModel


class SubmitModel(models.Model):
    fileSubmitted = models.FileField(verbose_name='File attachment', null=False, blank=False,
                                      upload_to='submits/%Y/%m/%d/',)
    description = models.CharField(verbose_name='Description of Vulnerability', max_length=1024)
    scanTask = models.ForeignKey(to=ScanTaskModel, on_delete=models.CASCADE, null=True, blank=True)
    dateCreated = models.DateTimeField(auto_now_add=True)