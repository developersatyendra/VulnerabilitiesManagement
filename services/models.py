from django.db import models
from django.contrib.auth.models import User
from django.core.validators import validate_comma_separated_integer_list


class ServiceModel(models.Model):
    createBy = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(verbose_name='Name of service', max_length=32)
    port = models.CharField(max_length=32, validators=[validate_comma_separated_integer_list])
    description = models.CharField(verbose_name='Description of service', max_length=128, blank=True)
    dateCreated = models.DateTimeField(auto_now_add=True, editable=True)
    dateUpdate = models.DateTimeField(auto_now=True, editable=True)

    class Meta:
        unique_together = ('name', 'port')

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name
