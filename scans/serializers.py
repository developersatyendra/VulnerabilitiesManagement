from rest_framework import serializers
from .models import ScanTaskModel, ScanInfoModel
from projects.serializers import ProjectNameSerializer


LEVEL_HIGH = 7  # High is >= LEVEL_HIGH
LEVEL_MED = 4   # Med is >= LEVEL_MED AND < LEVEL_HIGH
                # Low is > LEVEL_INFO AND < LEVEL_MED
LEVEL_INFO = 0  # Info is = LEVEL_INFO


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


# Serializer Scan Task with Vulnerabilities Information

class ScanVulnSerializer(serializers.ModelSerializer):
    high = serializers.SerializerMethodField()
    med = serializers.SerializerMethodField()
    low = serializers.SerializerMethodField()
    info = serializers.SerializerMethodField()
    numHost = serializers.SerializerMethodField()
    class Meta:
        model = ScanTaskModel
        fields = ['id', 'name', 'startTime', 'endTime', 'isProcessed', 'high', 'med', 'low', 'info', 'numHost']

    def get_high(self, obj):
        return obj.high

    def get_med(self, obj):
        return obj.med

    def get_low(self, obj):
        return obj.low

    def get_info(self, obj):
        return obj.info

    def get_numHost(self, obj):
        return obj.numHost


