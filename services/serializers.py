from rest_framework import serializers
from .models import ServiceModel


class ServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = ServiceModel
        fields = '__all__'


class ServiceNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = ServiceModel
        fields = ('id', 'name')