from rest_framework import serializers
from .models import TrackSource, ReportFolder, ReportEntry
from users.models import Project

class TrackSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackSource
        fields = [
            'id', 'name',
            'facebook_link', 'instagram_link', 'linkedin_link', 'tiktok_link', 
            'other_social_media',
            'project', 'created_at', 'updated_at'
        ]
    
    def create(self, validated_data):
        """
        Custom create method to ensure project ID is properly handled
        """
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """
        Custom update method to handle project ID updates
        """
        return super().update(instance, validated_data)

# Keep backward compatibility alias
TrackAccountSerializer = TrackSourceSerializer

class ReportEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportEntry
        fields = [
            'id', 'name', 'entity', 'posting_date',
            'platform_type', 'post_url', 'username', 'account_type', 'keywords',
            'content', 'post_id', 'track_source_id', 'created_at'
        ]

class ReportFolderSerializer(serializers.ModelSerializer):
    match_percentage = serializers.SerializerMethodField()
    entry_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ReportFolder
        fields = [
            'id', 'name', 'description', 'start_date', 'end_date', 
            'total_posts', 'matched_posts', 'match_percentage', 
            'entry_count', 'source_folders', 'project', 'created_at', 'updated_at'
        ]
    
    def get_match_percentage(self, obj):
        if obj.total_posts > 0:
            return round((obj.matched_posts / obj.total_posts) * 100)
        return 0
    
    def get_entry_count(self, obj):
        return obj.entries.count()

class ReportFolderDetailSerializer(ReportFolderSerializer):
    entries = ReportEntrySerializer(many=True, read_only=True)
    
    class Meta(ReportFolderSerializer.Meta):
        fields = ReportFolderSerializer.Meta.fields + ['entries'] 