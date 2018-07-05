from django.db import models
from hosts.models import HostModel
from services.models import ServiceModel
from django.contrib.auth.models import User
from projects.models import ScanProjectModel


class ScanTaskModel(models.Model):
    name = models.CharField(max_length=128, primary_key=True, verbose_name='Name of Scanning Task', unique=True)
    isProcessed = models.BooleanField(verbose_name='If this task is processed', default=False)
    description = models.CharField(verbose_name='Description of scanning task', max_length=1024)
    startTime = models.DateTimeField(verbose_name='Start time of Scanning Task')
    endTime = models.DateTimeField(verbose_name='Finish time of Scanning Task')
    fileAttachment = models.FileField(verbose_name='File attachment', blank=True)
    submitter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitter')
    scanBy = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scanBy')
    dateCreated = models.DateTimeField(auto_created=True)
    dateUpdate = models.DateTimeField(auto_now=True)
    scanProject = models.ForeignKey(to=ScanProjectModel,on_delete=models.CASCADE, blank=True)

    def __str__(self):
        return self.name