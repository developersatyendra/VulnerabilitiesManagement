from rest_framework import serializers
from .models import HostModel
from scans.models import ScanTaskModel


class HostSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='createBy.username')
    class Meta:
        model = HostModel
        fields = '__all__'


class HostNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = HostModel
        fields = ('id', 'hostName', 'ipAddr')


class HostVulnSerializer(serializers.ModelSerializer):
    high = serializers.SerializerMethodField()
    med = serializers.SerializerMethodField()
    low = serializers.SerializerMethodField()
    info = serializers.SerializerMethodField()

    idScan = serializers.SerializerMethodField()
    scanName = serializers.SerializerMethodField()
    startTime = serializers.SerializerMethodField()


    class Meta:
        model = HostModel
        fields = ['id', 'hostName', 'ipAddr', 'idScan', 'scanName', 'startTime', 'high', 'med', 'low', 'info']

    def get_high(self, obj):
        return obj.high

    def get_med(self, obj):
        return obj.med

    def get_low(self, obj):
        return obj.low

    def get_info(self, obj):
        return obj.info

    def get_idScan(self, obj):
        return obj.idScan

    def get_scanName(self, obj):
        return obj.scanName

    def get_startTime(self, obj):
        return obj.startTime