from rest_framework import serializers
from .models import BrightdataConfig, ScraperRequest, BatchScraperJob

class BrightdataConfigSerializer(serializers.ModelSerializer):
    """Serializer for Brightdata API configuration"""
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)
    
    class Meta:
        model = BrightdataConfig
        fields = ['id', 'name', 'platform', 'platform_display', 'api_token', 'dataset_id', 'is_active', 'description', 'created_at', 'updated_at']
        extra_kwargs = {
            'api_token': {'write_only': True}  # Hide the API token in responses
        }

class BatchScraperJobSerializer(serializers.ModelSerializer):
    """Serializer for Batch Scraper Jobs"""
    platforms_display = serializers.CharField(source='get_platforms_display', read_only=True)
    content_types_display = serializers.CharField(source='get_content_types_display', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = BatchScraperJob
        fields = [
            'id', 'name', 'project', 'project_name', 'source_folder_ids', 'platforms_to_scrape', 'platforms_display',
            'content_types_to_scrape', 'content_types_display',
            'num_of_posts', 'start_date', 'end_date', 'auto_create_folders', 'output_folder_pattern',
            'status', 'total_accounts', 'processed_accounts', 'successful_requests', 'failed_requests',
            'job_metadata', 'error_log', 'created_at', 'updated_at', 'started_at', 'completed_at'
        ]
        read_only_fields = ['total_accounts', 'processed_accounts', 'successful_requests', 'failed_requests', 'started_at', 'completed_at']

class BatchScraperJobCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating batch scraper jobs with simplified fields"""
    class Meta:
        model = BatchScraperJob
        fields = [
            'name', 'project', 'source_folder_ids', 'platforms_to_scrape', 'content_types_to_scrape',
            'num_of_posts', 'start_date', 'end_date', 'auto_create_folders', 'output_folder_pattern'
        ]

class ScraperRequestSerializer(serializers.ModelSerializer):
    """Serializer for Brightdata scraper requests"""
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)
    batch_job_name = serializers.CharField(source='batch_job.name', read_only=True)
    
    class Meta:
        model = ScraperRequest
        fields = [
            'id', 'config', 'batch_job', 'batch_job_name', 'request_id', 'platform', 'platform_display', 
            'content_type', 'target_url', 'account_name', 'iac_no', 'num_of_posts', 'posts_to_not_include', 
            'start_date', 'end_date', 'status', 'request_payload', 'response_metadata', 'error_message',
            'folder_id', 'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = ['request_id', 'status', 'response_metadata', 'error_message', 'completed_at']

class ScraperRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating scraper requests with simplified fields"""
    class Meta:
        model = ScraperRequest
        fields = [
            'platform', 'content_type', 'target_url', 'account_name', 'iac_no', 'num_of_posts',
            'posts_to_not_include', 'start_date', 'end_date', 'folder_id'
        ]
    
    def create(self, validated_data):
        # Get the platform-specific active config
        platform = validated_data.get('platform')
        try:
            config = BrightdataConfig.objects.filter(platform=platform, is_active=True).first()
            if not config:
                raise serializers.ValidationError(f"No active Brightdata configuration found for {platform}")
            
            # Add the config to the validated data
            validated_data['config'] = config
            
            # Create the scraper request
            return super().create(validated_data)
        except Exception as e:
            raise serializers.ValidationError(f"Error creating scraper request: {str(e)}") 