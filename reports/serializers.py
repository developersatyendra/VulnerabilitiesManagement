from rest_framework import serializers
from .models import ReportModel


LEVEL_HIGH = 7  # High is >= LEVEL_HIGH
LEVEL_MED = 4   # Med is >= LEVEL_MED AND < LEVEL_HIGH
                # Low is > LEVEL_INFO AND < LEVEL_MED
LEVEL_INFO = 0  # Info is = LEVEL_INFO


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportModel
        exclude = ('fileReport',)



