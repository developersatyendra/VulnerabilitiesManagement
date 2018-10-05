from django.db import models
from scans.models import ScanTaskModel
from django.contrib.auth.models import User
from projects.models import ScanProjectModel
from django.utils.deconstruct import deconstructible
from django.core.validators import FileExtensionValidator
from django.core.files.storage import FileSystemStorage
from django.conf import settings

STATUS = ['uploaded', 'processing', 'processed', 'duplicated', 'error']
SUBMIT_STORAGE = FileSystemStorage(getattr(settings, 'PATH_IMPORTED_FILES'))

# @deconstructible
# class ValidateValueInArray(object):
#     def __init__(self, array):
#         self.array = array
#
#     def __call__(self, value):
#        if value not in self.array:
#            raise ValidationError(
#                gettext_lazy('%(value)s is not in defined format'),
#                params={'value': value},
#            )
#        else:
#            return value


class SubmitModel(models.Model):
    """ Status of submitted files"""
    STATE_UPLOADED = 0
    STATE_PROCESSING = 1
    STATE_PROCESSED = 2
    STATE_DUPLICATED = 3
    STATE_ERROR = 4

    STATES = (
        (STATE_UPLOADED, "Uploaded"),
        (STATE_PROCESSING, "Processing"),
        (STATE_PROCESSED, "Processed"),
        (STATE_DUPLICATED, "Duplicated"),
        (STATE_ERROR, "Error")
    )

    fileSubmitted = models.FileField(verbose_name='File attachment', null=False, blank=False, validators=[FileExtensionValidator(allowed_extensions=['zip'])], storage=SUBMIT_STORAGE)
    description = models.CharField(verbose_name='Description of Vulnerability', max_length=1024, blank=True)
    project = models.ForeignKey(to=ScanProjectModel, on_delete=models.CASCADE)
    scanTask = models.ForeignKey(to=ScanTaskModel, on_delete=models.CASCADE, blank=True, null=True)
    submitter = models.ForeignKey(to=User, on_delete=models.CASCADE, blank=True)
    status = models.SmallIntegerField(verbose_name='Status of Submitted File', choices=STATES, default=STATE_UPLOADED, blank=True, null=True)
    dateCreated = models.DateTimeField(auto_now_add=True)
    dateUpdated = models.DateTimeField(auto_now=True)
