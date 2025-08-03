from rest_framework import serializers
from .models import InputCollection, WorkflowTask
from users.serializers import PlatformSerializer, ServiceSerializer, ProjectSerializer

class InputCollectionSerializer(serializers.ModelSerializer):
    platform_name = serializers.CharField(source='platform_name', read_only=True)
    service_name = serializers.CharField(source='service_name', read_only=True)
    url_count = serializers.IntegerField(source='url_count', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    platform_service_details = serializers.SerializerMethodField()
    
    class Meta:
        model = InputCollection
        fields = [
            'id', 'project', 'project_name', 'platform_service', 'platform_service_details',
            'platform_name', 'service_name', 'urls', 'url_count', 'status', 
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'platform_name', 'service_name', 'url_count']
    
    def get_platform_service_details(self, obj):
        if obj.platform_service:
            return {
                'platform': PlatformSerializer(obj.platform_service.platform).data,
                'service': ServiceSerializer(obj.platform_service.service).data,
                'is_enabled': obj.platform_service.is_enabled
            }
        return None
    
    def validate_urls(self, value):
        """Validate that URLs is a list and not empty"""
        if not isinstance(value, list):
            raise serializers.ValidationError("URLs must be a list")
        if len(value) == 0:
            raise serializers.ValidationError("At least one URL is required")
        return value

class WorkflowTaskSerializer(serializers.ModelSerializer):
    input_collection_details = InputCollectionSerializer(source='input_collection', read_only=True)
    batch_job_name = serializers.CharField(source='batch_job.name', read_only=True)
    batch_job_status = serializers.CharField(source='batch_job.status', read_only=True)
    
    class Meta:
        model = WorkflowTask
        fields = [
            'id', 'input_collection', 'input_collection_details', 'batch_job', 
            'batch_job_name', 'batch_job_status', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'batch_job_name', 'batch_job_status']

class InputCollectionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating input collections with automatic workflow task creation"""
    
    class Meta:
        model = InputCollection
        fields = ['project', 'platform_service', 'urls']
    
    def create(self, validated_data):
        # Set the created_by user
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data) 