from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from hosts.models import HostModel
from scans.models import ScanTaskModel
from services.models import ServiceModel


class VulnerabilityModel(models.Model):
    levelRisk = models.IntegerField(verbose_name='Level of Risk', validators=[MinValueValidator(0), MaxValueValidator(3)])
    summary = models.CharField(verbose_name='Summary of Vulnerability', max_length=512)
    description = models.CharField(verbose_name='Description of Vulnerability', max_length=1024)
    scanTask = models.ForeignKey(to=ScanTaskModel, on_delete=models.CASCADE)
    hostScanned = models.ForeignKey(to=HostModel, on_delete=models.CASCADE)
    service = models.ForeignKey(to=ServiceModel, on_delete=models.CASCADE)