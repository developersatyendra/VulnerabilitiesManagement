from django.contrib import admin
from .models import ScanTaskModel, HostScanInfoModel

admin.site.register(ScanTaskModel)
admin.site.register(HostScanInfoModel)