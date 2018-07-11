from django.db import models
from django.contrib.auth.models import User


class HostModel(models.Model):
    createBy = models.ForeignKey(User, on_delete=models.CASCADE)
    ipAdr = models.GenericIPAddressField(unique=True)
    hostName = models.CharField(max_length=128, unique=True)
    platform = models.CharField(max_length=64, blank=True)
    osName = models.CharField(max_length=128, blank=True)
    osVersion = models.CharField(max_length=128, blank=True)
    description = models.CharField(verbose_name='Description of Host', max_length=128, blank=True)
    dateCreated = models.DateTimeField(auto_now_add=True)
    dateUpdate = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.hostName

    def __unicode__(self):
        return self.hostName
