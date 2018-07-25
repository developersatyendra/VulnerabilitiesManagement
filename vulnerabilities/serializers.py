from rest_framework import serializers
from services.serializers import ServiceNameSerializer
from .models import VulnerabilityModel


class VulnSerializer(serializers.ModelSerializer):
    service = ServiceNameSerializer(read_only=True, many=False)

    class Meta:
        model = VulnerabilityModel
        fields = '__all__'

