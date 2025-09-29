from rest_framework import serializers
from .models import ApifyConfig, ApifyBatchJob, ApifyScraperRequest, ApifyNotification, ApifyWebhookEvent

class ApifyConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApifyConfig
        fields = '__all__'

class ApifyBatchJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApifyBatchJob
        fields = '__all__'

class ApifyScraperRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApifyScraperRequest
        fields = '__all__'

class ApifyNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApifyNotification
        fields = '__all__'

class ApifyWebhookEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApifyWebhookEvent
        fields = '__all__'
