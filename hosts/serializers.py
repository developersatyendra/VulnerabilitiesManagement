from rest_framework import serializers
from .models import HostModel


class HostSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='createBy.username')
    class Meta:
        model = HostModel
        fields = '__all__'


class HostNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = HostModel
        fields = ('id', 'hostName')