from django.contrib import admin
from .models import TrackSource, TrackAccount, ReportFolder, ReportEntry

@admin.register(TrackSource)
class TrackSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'iac_no', 'facebook_link', 'instagram_link', 'linkedin_link', 'tiktok_link', 
                   'risk_classification', 'close_monitoring', 'project')
    list_filter = ('risk_classification', 'close_monitoring', 'posting_frequency', 'project')
    search_fields = ('name', 'iac_no')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('name',)
    raw_id_fields = ('project',)
    list_select_related = ('project',)

# Keep backward compatibility alias
TrackAccountAdmin = TrackSourceAdmin

@admin.register(ReportFolder)
class ReportFolderAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'total_posts', 'matched_posts', 'get_match_percentage', 'project', 'created_at')
    list_filter = ('project', 'start_date', 'end_date')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'total_posts', 'matched_posts')
    ordering = ('-created_at',)
    raw_id_fields = ('project',)
    list_select_related = ('project',)
    
    def get_match_percentage(self, obj):
        if obj.total_posts > 0:
            return f"{round((obj.matched_posts / obj.total_posts) * 100)}%"
        return "0%"
    get_match_percentage.short_description = 'Match Percentage'

@admin.register(ReportEntry)
class ReportEntryAdmin(admin.ModelAdmin):
    list_display = ('username', 'name', 'iac_no', 'platform_type', 'posting_date', 'track_source_id')
    list_filter = ('platform_type', 'close_monitoring', 'report')
    search_fields = ('name', 'iac_no', 'username', 'content')
    readonly_fields = ('created_at',)
    ordering = ('-posting_date',)
    raw_id_fields = ('report',)
    list_select_related = ('report',)
