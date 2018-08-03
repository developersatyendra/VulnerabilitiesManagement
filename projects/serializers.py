from rest_framework import serializers
from .models import ScanProjectModel


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = ScanProjectModel
        fields = "__all__"


class ProjectNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = ScanProjectModel
        fields = ('id', 'name')