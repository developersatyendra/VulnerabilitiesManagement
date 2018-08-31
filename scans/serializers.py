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


# Serializer Scan Task with Vulnerabilities Information

class ScanVulnSerializer(serializers.ModelSerializer):
    vulnerabilities = serializers.SerializerMethodField()
    numHost = serializers.SerializerMethodField()
    class Meta:
        model = ScanTaskModel
        fields = ['id', 'name', 'startTime', 'endTime', 'isProcessed', 'vulnerabilities', 'numHost']
        depth = 3

    def get_attribute(self, obj):
        obj.acb = "Test"
        return obj

    def get_vulnerabilities(self, obj):
        if self.context and self.context['advFilter'] == 'hostID':
            vuln = obj.scanInfo.get(Q(hostScanned__id=self.context['advFilterValue'])).vulnFound
            high = vuln.filter(levelRisk__gte=LEVEL_HIGH).count()
            med = vuln.filter(Q(levelRisk__gte=LEVEL_MED) & Q(levelRisk__lt=LEVEL_HIGH)).count()
            low = vuln.filter(Q(levelRisk__gt=LEVEL_INFO) & Q(levelRisk__lt=LEVEL_MED)).count()
            info = vuln.filter(levelRisk=LEVEL_INFO).count()
        else:
            for scanInfo in obj.scanInfo.all():
                vulnIDs = scanInfo.vulnFound.all().values_list("id", flat=True)
                vuln = VulnerabilityModel.objects.filter(id__in=vulnIDs)
                high = vuln.filter(levelRisk__gte=LEVEL_HIGH).count()
                med = vuln.filter(Q(levelRisk__gte=LEVEL_MED)&Q(levelRisk__lt=LEVEL_HIGH)).count()
                low = vuln.filter(Q(levelRisk__gt=LEVEL_INFO) & Q(levelRisk__lt=LEVEL_MED)).count()
                info = vuln.filter(levelRisk=LEVEL_INFO).count()
        return {'high': high, 'medium': med, 'low': low, 'information': info}

    def get_numHost(self, obj):
        return obj.scanInfo.all().count()


