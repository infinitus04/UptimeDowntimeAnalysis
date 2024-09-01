from .models import *
from rest_framework.serializers import ModelSerializer

class TimeStampSerializer(ModelSerializer):
    class Meta:
        model = TimeStamp
        fields = ['store', 'status', 'timestamp_utc']

class ReportSerializer(ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'status']