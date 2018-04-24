from django.db import models
from vulnerabilities.models import VulnerabilityModel
from hosts.models import HostModel
from services.models import ServiceModel
from django.contrib.auth.models import User


class HostScanInfoModel(models.Model):
    isSuccess = models.BooleanField(verbose_name='if this host is scanned', default=False)
    host = models.OneToOneField(to=HostModel, on_delete=models.CASCADE)
    service = models.ForeignKey(to=ServiceModel, on_delete=models.CASCADE, blank=True)
    vulnerability = models.ForeignKey(to=VulnerabilityModel, on_delete=models.CASCADE, blank=True)


class ScanTaskModel(models.Model):
    name = models.CharField(max_length=128, primary_key=True, verbose_name='Name of Scanning Task')
    isProcessed = models.BooleanField(verbose_name='If this task is processed', default=False)
    description = models.CharField(verbose_name='Description of scanning task', max_length=1024)
    startTime = models.DateTimeField(verbose_name='Start time of Scanning Task')
    endTime = models.DateTimeField(verbose_name='Finish time of Scanning Task')
    fileAttachment = models.FileField(verbose_name='File attachment', blank=True)
    submitter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitter')
    scanBy = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scanBy')
    hostScanInfo = models.ForeignKey(HostScanInfoModel, on_delete=models.CASCADE)
    dateCreated = models.DateTimeField(auto_created=True)
    dateUpdate = models.DateTimeField(auto_now=True)