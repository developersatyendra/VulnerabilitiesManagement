from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class VulnerabilityModel(models.Model):
    levelRisk = models.IntegerField(verbose_name='Level of Risk', validators=[MinValueValidator(0), MaxValueValidator(4)])
    summary = models.CharField(verbose_name='Summary of Vulnerability', max_length=512)
    description = models.CharField(verbose_name='Description of Vulnerability', max_length=1024)