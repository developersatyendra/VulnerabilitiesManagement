from django.db import models
from services.models import ServiceModel
from django.contrib.auth.models import User


class HostModel(models.Model):
    hostName = models.CharField(max_length=128)
    ipAddr = models.GenericIPAddressField(unique=True)
    createBy = models.ForeignKey(User, on_delete=models.CASCADE)
    osName = models.CharField(max_length=128, blank=True)
    osVersion = models.CharField(max_length=128, blank=True)
    description = models.CharField(verbose_name='Description of Host', max_length=128, blank=True)
    dateCreated = models.DateTimeField(auto_now_add=True)
    dateUpdate = models.DateTimeField(auto_now=True)
    services = models.ManyToManyField(ServiceModel, related_name='ServiceHost')

    def __str__(self):
        return self.hostName + ' - ' + self.ipAddr

    def __unicode__(self):
        return self.hostName + ' - ' + self.ipAddr
