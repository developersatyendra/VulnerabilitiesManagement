from rest_framework import serializers
from .models import ScanTaskModel, ScanInfoModel
from vulnerabilities.models import VulnerabilityModel
from projects.serializers import ProjectNameSerializer
from django.db.models import Q


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


class ScanVulnSerializer(serializers.ModelSerializer):
    # vulnCount = serializers.IntegerField(source='scanInfo_vulnFound.count')?
    # scanInfo = ScanInfoSerializer(read_only=True, many=True)

    vulnerabilities = serializers.SerializerMethodField()
    numHost = serializers.SerializerMethodField()
    class Meta:
        model = ScanTaskModel
        fields = ['id', 'name', 'vulnerabilities' ,'numHost']
        depth = 3

    def get_attribute(self, obj):
        obj.acb = "Test"
        return obj

    def get_vulnerabilities(self, obj):
        for scanInfo in obj.scanInfo.all():
            vulnIDs = scanInfo.vulnFound.all().values_list("id", flat=True)
            high = VulnerabilityModel.objects.filter(Q(id__in=vulnIDs)&Q(levelRisk__gte=LEVEL_HIGH)).count()
            med = VulnerabilityModel.objects.filter(Q(id__in=vulnIDs)&Q(levelRisk__gte=LEVEL_MED)&Q(levelRisk__lt=LEVEL_MED)).count()
            low = VulnerabilityModel.objects.filter(
                Q(id__in=vulnIDs) & Q(levelRisk__gt=LEVEL_INFO) & Q(levelRisk__lt=LEVEL_MED)).count()
            info = VulnerabilityModel.objects.filter(Q(id__in=vulnIDs) & Q(levelRisk=LEVEL_INFO)).count()
        return {'high':high, 'medium':med, 'low':low, 'information':info}

    def get_numHost(self, obj):
        return obj.scanInfo.all().count()