from rest_framework import serializers
from .models import BrightdataConfig, ScraperRequest

class BrightdataConfigSerializer(serializers.ModelSerializer):
    """Serializer for Brightdata API configuration"""
    class Meta:
        model = BrightdataConfig
        fields = ['id', 'name', 'api_token', 'dataset_id', 'is_active', 'created_at', 'updated_at']
        extra_kwargs = {
            'api_token': {'write_only': True}  # Hide the API token in responses
        }

class ScraperRequestSerializer(serializers.ModelSerializer):
    """Serializer for Brightdata scraper requests"""
    class Meta:
        model = ScraperRequest
        fields = [
            'id', 'config', 'request_id', 'platform', 'content_type', 'target_url',
            'num_of_posts', 'posts_to_not_include', 'start_date', 'end_date',
            'status', 'request_payload', 'response_metadata', 'error_message',
            'folder_id', 'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = ['request_id', 'status', 'response_metadata', 'error_message', 'completed_at']

class ScraperRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating scraper requests with simplified fields"""
    class Meta:
        model = ScraperRequest
        fields = [
            'platform', 'content_type', 'target_url', 'num_of_posts',
            'posts_to_not_include', 'start_date', 'end_date', 'folder_id'
        ]
    
    def create(self, validated_data):
        # Get the default active config
        try:
            config = BrightdataConfig.objects.filter(is_active=True).first()
            if not config:
                raise serializers.ValidationError("No active Brightdata configuration found")
            
            # Add the config to the validated data
            validated_data['config'] = config
            
            # Create the scraper request
            return super().create(validated_data)
        except Exception as e:
            raise serializers.ValidationError(f"Error creating scraper request: {str(e)}") 