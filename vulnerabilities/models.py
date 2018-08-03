from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from hosts.models import HostModel
from services.models import ServiceModel


class VulnerabilityModel(models.Model):
    name = models.CharField(verbose_name='Name of Vulnerability', max_length=128, unique=True)
    levelRisk = models.FloatField(verbose_name='Level of Risk', validators=[MinValueValidator(0), MaxValueValidator(10)])
    description = models.CharField(verbose_name='Description of Vulnerability', max_length=5000, blank=True)
    observation = models.CharField(verbose_name='Observation of Vulnerability', max_length=5000, blank=True)
    recommendation = models.CharField(verbose_name='Recommendation of Vulnerability', max_length=5000, blank=True)
    cve = models.CharField(verbose_name='CVE of Vulnerability', max_length=24, blank=True)
    service = models.ForeignKey(to=ServiceModel, on_delete=models.CASCADE)