# serializers.py trong module subscriptions
from rest_framework import serializers
from .models import SessionUsage

class SessionUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionUsage
        fields = ['id', 'used_sessions', 'usage_date']
