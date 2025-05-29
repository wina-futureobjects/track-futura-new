from rest_framework import serializers
from .models import InstagramPost, Folder, InstagramComment, CommentScrapingJob

class FolderSerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()
    reel_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    category_display = serializers.ReadOnlyField()
    
    class Meta:
        model = Folder
        fields = ['id', 'name', 'description', 'category', 'category_display', 'project', 'created_at', 'updated_at', 'post_count', 'reel_count', 'comment_count']
    
    def create(self, validated_data):
        """
        Custom create method to ensure project ID is properly handled
        """
        # Extract project from validated data
        project = validated_data.get('project')
        
        # If no project is provided but it's required, try to get from context
        if not project:
            request = self.context.get('request')
            if request and hasattr(request, 'data'):
                project_id = request.data.get('project')
                if project_id:
                    from users.models import Project
                    try:
                        project = Project.objects.get(id=project_id)
                        validated_data['project'] = project
                    except Project.DoesNotExist:
                        pass
        
        # Create the folder
        folder = Folder.objects.create(**validated_data)
        
        # Double-check project assignment (failsafe)
        if not folder.project_id and project:
            folder.project = project
            folder.save()
        
        return folder
    
    def update(self, instance, validated_data):
        """
        Custom update method to ensure project ID is preserved
        """
        # If project is not in validated_data, preserve the existing one
        if 'project' not in validated_data and instance.project:
            validated_data['project'] = instance.project
        
        # Update the instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance
    
    def get_post_count(self, obj):
        return obj.posts.filter(content_type='post').count()
    
    def get_reel_count(self, obj):
        return obj.posts.filter(content_type='reel').count()
    
    def get_comment_count(self, obj):
        return obj.comments.count()

class InstagramPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstagramPost
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class InstagramCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstagramComment
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class CommentScrapingJobSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    result_folder_name = serializers.CharField(source='result_folder.name', read_only=True)
    
    class Meta:
        model = CommentScrapingJob
        fields = [
            'id', 'name', 'project', 'selected_folders', 'status', 'status_display',
            'total_posts', 'processed_posts', 'successful_requests', 'failed_requests',
            'total_comments_scraped', 'brightdata_job_id', 'error_log',
            'result_folder', 'result_folder_name', 'created_at', 'updated_at',
            'started_at', 'completed_at'
        ]
        read_only_fields = (
            'created_at', 'updated_at', 'started_at', 'completed_at',
            'status', 'total_posts', 'processed_posts', 'successful_requests',
            'failed_requests', 'total_comments_scraped', 'brightdata_job_id',
            'error_log'
        ) 