from django.contrib import admin
from .models import ScanTaskModel, ScanInfoModel

admin.site.register(ScanTaskModel)
admin.site.register(ScanInfoModel)