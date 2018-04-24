from django.db import models
from scans.models import ScanTaskModel
from django.contrib.auth.models import User


class ScanProjectModel(models.Model):
    createBy = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(verbose_name='Name of Scanning Project', max_length=64, primary_key=True)
    description = models.CharField(verbose_name='Description of scanning project', max_length=1024)
    createDate = models.DateField(verbose_name='Date of create project', auto_now_add=True)
    scanTask = models.ForeignKey(ScanTaskModel, on_delete=models.CASCADE)
    dateCreated = models.DateTimeField(auto_created=True)
    dateUpdate = models.DateTimeField(auto_now=True)