from rest_framework import serializers
from .models import ScanTaskModel, ScanInfoModel
from projects.serializers import ProjectNameSerializer


class ScanSerializer(serializers.ModelSerializer):
    scanProject = ProjectNameSerializer(read_only=True, many=False)
    fileAttachment = serializers.FileField(max_length=None, use_url=True)

    class Meta:
        model = ScanTaskModel
        fields = '__all__'


class ScanNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScanTaskModel
        fields = ['id', 'name']


class ScanInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScanInfoModel
        fields = '__all__'
