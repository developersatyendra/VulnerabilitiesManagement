from rest_framework import serializers
from hosts.serializers import HostNameSerializer
from services.serializers import ServiceNameSerializer
from .models import VulnerabilityModel


class VulnSerializer(serializers.ModelSerializer):
    hostScanned = HostNameSerializer(read_only=True, many=False)
    service = ServiceNameSerializer(read_only=True, many=False)

    class Meta:
        model = VulnerabilityModel
        fields = '__all__'


class VulnExtendSerializer(serializers.Serializer):
    levelRisk = serializers.DecimalField
    summary = serializers.CharField(max_length=512)
    scanTask = serializers.CharField(max_length=512)
    hostScanned = serializers.CharField(max_length=512)
    service = serializers.DecimalField
    description = serializers.CharField(max_length=1024)
    ServiceModel__name = serializers.CharField(max_length=512)
    HostModel__ipAdr = serializers.CharField(max_length=512)
    HostModel__hostName = serializers.CharField(max_length=512)