from rest_framework import serializers
from .models import SubmitModel
from scans.serializers import ScanSerializer
from projects.serializers import ProjectSerializer


class SubmitSerializer(serializers.ModelSerializer):
    scanTask = ScanSerializer(read_only=True, many=False)
    fileSubmitted = serializers.FileField(max_length=None, use_url=True)
    project = ProjectSerializer(read_only=True, many=False)
    class Meta:
        model = SubmitModel
        fields = '__all__'


class SubmitNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmitModel
        fields = ['id','name']