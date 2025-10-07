"""
BrightData Integration Serializers

This module provides serializers for BrightData integration models.
"""

from rest_framework import serializers
from .models import BrightDataConfig, BrightDataBatchJob, BrightDataScraperRequest, BrightDataWebhookEvent


class BrightDataConfigSerializer(serializers.ModelSerializer):
    """Serializer for BrightData configuration"""
    
    class Meta:
        model = BrightDataConfig
        fields = ['id', 'name', 'platform', 'dataset_id', 'api_token', 'is_active', 'created_at', 'updated_at']
        extra_kwargs = {
            'api_token': {'write_only': True}  # Hide API token in responses
        }


class BrightDataScraperRequestSerializer(serializers.ModelSerializer):
    """Serializer for BrightData scraper requests"""
    
    config_name = serializers.CharField(source='config.name', read_only=True)
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)
    
    class Meta:
        model = BrightDataScraperRequest
        fields = [
            'id', 'config', 'config_name', 'batch_job', 'platform', 'platform_display',
            'content_type', 'target_url', 'source_name', 'request_id', 'snapshot_id',
            'dataset_id', 'status', 'error_message', 'created_at', 'updated_at',
            'started_at', 'completed_at'
        ]
        read_only_fields = ['request_id', 'snapshot_id', 'dataset_id', 'started_at', 'completed_at']


class BrightDataBatchJobSerializer(serializers.ModelSerializer):
    """Serializer for BrightData batch jobs"""
    
    scraper_requests = BrightDataScraperRequestSerializer(many=True, read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    duration = serializers.SerializerMethodField()
    request_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BrightDataBatchJob
        fields = [
            'id', 'name', 'project', 'project_name', 'source_folder_ids',
            'platforms_to_scrape', 'content_types_to_scrape', 'platform_params',
            'num_of_posts', 'start_date', 'end_date', 'status', 'error_log',
            'progress', 'created_by', 'created_at', 'updated_at', 'started_at',
            'completed_at', 'duration', 'request_count', 'scraper_requests'
        ]
        read_only_fields = ['progress', 'started_at', 'completed_at', 'duration', 'request_count']
    
    def get_duration(self, obj):
        """Get formatted duration string"""
        duration = obj.duration
        if duration:
            total_seconds = int(duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            
            if hours > 0:
                return f"{hours}h {minutes}m {seconds}s"
            elif minutes > 0:
                return f"{minutes}m {seconds}s"
            else:
                return f"{seconds}s"
        return None
    
    def get_request_count(self, obj):
        """Get count of scraper requests"""
        return obj.scraper_requests.count()


class BrightDataWebhookEventSerializer(serializers.ModelSerializer):
    """Serializer for BrightData webhook events"""
    
    class Meta:
        model = BrightDataWebhookEvent
        fields = [
            'id', 'event_id', 'snapshot_id', 'status', 'platform',
            'raw_data', 'processed_at', 'created_at'
        ]
        read_only_fields = ['processed_at', 'created_at']