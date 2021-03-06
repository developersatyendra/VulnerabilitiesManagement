from django.db import models
from django.contrib.auth.models import User


class ScanProjectModel(models.Model):
    createBy = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(verbose_name='Name of Scanning Project', max_length=64, unique=True)
    description = models.CharField(verbose_name='Description of scanning project', blank=True, max_length=1024)
    dateCreated = models.DateTimeField(verbose_name='Date of create project', auto_now_add=True)
    dateUpdate = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name