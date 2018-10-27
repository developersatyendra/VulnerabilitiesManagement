from rest_framework import serializers
from .models import ScanProjectModel


class ProjectSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='createBy.username')
    class Meta:
        model = ScanProjectModel
        fields = "__all__"


class ProjectNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = ScanProjectModel
        fields = ('id', 'name')


class ProjectVulnSerializer(serializers.ModelSerializer):
    high = serializers.SerializerMethodField()
    med = serializers.SerializerMethodField()
    low = serializers.SerializerMethodField()
    info = serializers.SerializerMethodField()
    numScanTasks = serializers.SerializerMethodField()
    class Meta:
        model = ScanProjectModel
        fields = ['id', 'name', 'high', 'med', 'low', 'info', 'numScanTasks']

    def get_high(self, obj):
        return obj.high

    def get_med(self, obj):
        return obj.med

    def get_low(self, obj):
        return obj.low

    def get_info(self, obj):
        return obj.info

    def get_numScanTasks(self, obj):
        return obj.numScanTasks
