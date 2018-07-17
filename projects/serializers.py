from rest_framework import serializers
from .models import ScanProjectModel


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = ScanProjectModel
        fields = "__all__"