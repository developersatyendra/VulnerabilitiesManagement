from rest_framework import serializers
from .models import ScanTaskModel
from projects.serializers import ProjectSerializer


class ScanSerializer(serializers.ModelSerializer):
    scanProject = ProjectSerializer(read_only=True, many=False)
    fileAttachment = serializers.FileField(max_length=None, use_url=True)
    class Meta:
        model = ScanTaskModel
        fields = '__all__'

class ScanNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScanTaskModel
        fields = ['id','name']