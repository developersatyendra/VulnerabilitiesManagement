from django.db import models
from django.contrib.auth.models import User


class HostModel(models.Model):
    createBy = models.OneToOneField(User, on_delete=models.CASCADE)
    ipAdr = models.GenericIPAddressField(unique=True, primary_key=True)
    hostName = models.CharField(max_length=128, unique=True)
    platform = models.CharField(max_length=64, blank=True)
    osNAme = models.CharField(max_length=128, blank=True)
    dateCreated = models.DateTimeField(auto_created=True)
    dateUpdate = models.DateTimeField(auto_now=True)
