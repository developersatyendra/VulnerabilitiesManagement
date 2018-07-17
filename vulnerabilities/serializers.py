from rest_framework import serializers
from hosts.serializers import HostNameSerializer
from services.serializers import ServiceNameSerializer
from scans.serializers import ScanNameSerializer
from .models import VulnerabilityModel


class VulnSerializer(serializers.ModelSerializer):
    hostScanned = HostNameSerializer(read_only=True, many=False)
    service = ServiceNameSerializer(read_only=True, many=False)
    scanTask = ScanNameSerializer(read_only=True, many=False)
    class Meta:
        model = VulnerabilityModel
        fields = '__all__'