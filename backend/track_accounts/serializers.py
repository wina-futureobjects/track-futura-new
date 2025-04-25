from rest_framework import serializers
from .models import TrackAccount, TrackAccountFolder, ReportFolder, ReportEntry

class TrackAccountFolderSerializer(serializers.ModelSerializer):
    account_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TrackAccountFolder
        fields = ['id', 'name', 'description', 'account_count', 'created_at', 'updated_at']
    
    def get_account_count(self, obj):
        return obj.accounts.count()

class TrackAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackAccount
        fields = [
            'id', 'name', 'iac_no', 
            'facebook_username', 'instagram_username', 'linkedin_username', 'tiktok_username',
            'facebook_id', 'instagram_id', 'linkedin_id', 'tiktok_id', 
            'other_social_media', 'risk_classification', 'close_monitoring', 'posting_frequency',
            'folder', 'created_at', 'updated_at'
        ]

class ReportEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportEntry
        fields = [
            'id', 'name', 'iac_no', 'entity', 'close_monitoring', 'posting_date',
            'platform_type', 'post_url', 'username', 'account_type', 'keywords',
            'content', 'post_id', 'track_account_id', 'created_at'
        ]

class ReportFolderSerializer(serializers.ModelSerializer):
    match_percentage = serializers.SerializerMethodField()
    entry_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ReportFolder
        fields = [
            'id', 'name', 'description', 'start_date', 'end_date', 
            'total_posts', 'matched_posts', 'match_percentage', 
            'entry_count', 'source_folders', 'created_at', 'updated_at'
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