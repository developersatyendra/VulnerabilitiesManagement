from rest_framework import serializers
from .models import ScanTaskModel, ScanInfoModel
from projects.serializers import ProjectNameSerializer


class ScanSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='submitter.username')
    scanProject = ProjectNameSerializer(read_only=True, many=False)

    class Meta:
        model = ScanTaskModel
        exclude = ('fileAttachment',)


class ScanNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScanTaskModel
        fields = ['id', 'name']


class ScanAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScanTaskModel
        fields = ['id', 'fileAttachment']


class ScanInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScanInfoModel
        fields = '__all__'
