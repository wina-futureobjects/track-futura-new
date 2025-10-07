from rest_framework import serializers
from .models import TrackSource, SourceFolder, ReportFolder, ReportEntry, UnifiedRunFolder
from users.models import Project

class SourceFolderSerializer(serializers.ModelSerializer):
    source_count = serializers.SerializerMethodField()
    folder_type_display = serializers.CharField(source='get_folder_type_display', read_only=True)

    class Meta:
        model = SourceFolder
        fields = [
            'id', 'name', 'description', 'folder_type', 'folder_type_display',
            'project', 'source_count', 'created_at', 'updated_at'
        ]

    def get_source_count(self, obj):
        # Check if this is for report marketplace (show post counts) or input collection (show source counts)
        request = self.context.get('request')
        
        # If request has 'for_reports' parameter or comes from reports module, show post counts
        if request and (
            request.GET.get('for_reports') == 'true' or
            'report' in request.path.lower()
        ):
            # For report marketplace, return the actual post count from the mapped data folders
            if 'Nike' in obj.name:
                # Nike data is in Facebook folder 21
                try:
                    from facebook_data.models import Folder as FacebookFolder
                    nike_folder = FacebookFolder.objects.get(id=21)
                    return nike_folder.posts.count()
                except:
                    pass
            elif 'Adidas' in obj.name:
                # Adidas data is in Facebook folder 20
                try:
                    from facebook_data.models import Folder as FacebookFolder
                    adidas_folder = FacebookFolder.objects.get(id=20)
                    return adidas_folder.posts.count()
                except:
                    pass
        
        # Default: Return the number of TrackSources (input sources) in this folder
        return obj.sources.count()

class TrackSourceSerializer(serializers.ModelSerializer):
    folder_name = serializers.CharField(source='folder.name', read_only=True, allow_null=True)
    folder_type = serializers.CharField(source='folder.folder_type', read_only=True, allow_null=True)

    class Meta:
        model = TrackSource
        fields = [
            'id', 'name',
            'platform', 'service_name',
            'facebook_link', 'instagram_link', 'linkedin_link', 'tiktok_link',
            'other_social_media',
            'url_count',
            'folder', 'folder_name', 'folder_type',
            'project', 'created_at', 'updated_at'
        ]

    def _normalize_service_name(self, service_name):
        """
        Normalize service name from frontend format to backend format
        Frontend sends: instagram_posts, facebook_pages_posts, linkedin_posts, tiktok_posts
        Backend expects: posts, reels, comments
        """
        if not service_name:
            return service_name
            
        # Remove platform prefix and normalize
        if service_name.startswith('instagram_'):
            return service_name.replace('instagram_', '')
        elif service_name.startswith('facebook_'):
            # Handle facebook_pages_posts -> posts
            if service_name == 'facebook_pages_posts':
                return 'posts'
            elif service_name == 'facebook_reels_profile':
                return 'reels'
            else:
                return service_name.replace('facebook_', '')
        elif service_name.startswith('linkedin_'):
            return service_name.replace('linkedin_', '')
        elif service_name.startswith('tiktok_'):
            return service_name.replace('tiktok_', '')
        else:
            return service_name
    
    def create(self, validated_data):
        """
        Custom create method to ensure project ID is properly handled and service_name is normalized
        """
        # Normalize service_name if provided
        if 'service_name' in validated_data:
            validated_data['service_name'] = self._normalize_service_name(validated_data['service_name'])
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """
        Custom update method to handle project ID updates and service_name normalization
        """
        # Normalize service_name if provided
        if 'service_name' in validated_data:
            validated_data['service_name'] = self._normalize_service_name(validated_data['service_name'])
        
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

class UnifiedRunFolderSerializer(serializers.ModelSerializer):
    platform = serializers.SerializerMethodField()
    category_display = serializers.SerializerMethodField()
    subfolders = serializers.SerializerMethodField()
    post_count = serializers.SerializerMethodField()
    
    class Meta:
        model = UnifiedRunFolder
        fields = [
            'id', 'name', 'description', 'folder_type', 'category', 'category_display',
            'platform_code', 'service_code', 'project', 'scraping_run', 'parent_folder',
            'platform', 'subfolders', 'post_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'platform', 'category_display', 'subfolders', 'post_count', 'created_at', 'updated_at']
    
    def get_platform(self, obj):
        # Return the actual platform code if available, otherwise 'unified'
        return obj.platform_code or 'unified'
    
    def get_category_display(self, obj):
        # Return a human-readable category name
        category_display_map = {
            'posts': 'Posts',
            'reels': 'Reels', 
            'comments': 'Comments'
        }
        return category_display_map.get(obj.category, obj.category.title())
    
    def get_subfolders(self, obj):
        # Get direct subfolders (UnifiedRunFolder children) and serialize them recursively
        subfolders_data = UnifiedRunFolderSerializer(obj.subfolders.all(), many=True, context=self.context).data

        # If this is a job folder, also include linked platform-specific folders
        if obj.folder_type == 'job':
            platform_folders = []

            # Check for linked Instagram folders
            try:
                from instagram_data.models import Folder as IGFolder
                from instagram_data.serializers import FolderSerializer as IGFolderSerializer
                ig_folders = IGFolder.objects.filter(unified_job_folder=obj)
                if ig_folders.exists():
                    platform_folders.extend(IGFolderSerializer(ig_folders, many=True, context=self.context).data)
            except Exception as e:
                pass

            # Check for linked Facebook folders
            try:
                from facebook_data.models import Folder as FBFolder
                from facebook_data.serializers import FolderSerializer as FBFolderSerializer
                fb_folders = FBFolder.objects.filter(unified_job_folder=obj)
                if fb_folders.exists():
                    platform_folders.extend(FBFolderSerializer(fb_folders, many=True, context=self.context).data)
            except Exception as e:
                pass

            # Check for linked LinkedIn folders
            try:
                from linkedin_data.models import Folder as LIFolder
                from linkedin_data.serializers import FolderSerializer as LIFolderSerializer
                li_folders = LIFolder.objects.filter(unified_job_folder=obj)
                if li_folders.exists():
                    platform_folders.extend(LIFolderSerializer(li_folders, many=True, context=self.context).data)
            except Exception as e:
                pass

            # Check for linked TikTok folders
            try:
                from tiktok_data.models import Folder as TTFolder
                from tiktok_data.serializers import FolderSerializer as TTFolderSerializer
                tt_folders = TTFolder.objects.filter(unified_job_folder=obj)
                if tt_folders.exists():
                    platform_folders.extend(TTFolderSerializer(tt_folders, many=True, context=self.context).data)
            except Exception as e:
                pass

            # Combine unified subfolders with platform-specific folders
            subfolders_data = list(subfolders_data) + platform_folders

        return subfolders_data
    
    def get_post_count(self, obj):
        return obj.get_content_count() 