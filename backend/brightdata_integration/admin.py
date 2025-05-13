from django.contrib import admin
from .models import BrightdataConfig, ScraperRequest

@admin.register(BrightdataConfig)
class BrightdataConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'dataset_id', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'dataset_id')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ScraperRequest)
class ScraperRequestAdmin(admin.ModelAdmin):
    list_display = ('platform', 'content_type', 'target_url', 'status', 'created_at', 'completed_at')
    list_filter = ('platform', 'content_type', 'status')
    search_fields = ('target_url', 'request_id')
    readonly_fields = ('created_at', 'updated_at', 'completed_at', 'request_payload', 'response_metadata')
    fieldsets = (
        ('Request Info', {
            'fields': ('config', 'platform', 'content_type', 'target_url', 'num_of_posts', 
                       'posts_to_not_include', 'start_date', 'end_date', 'folder_id')
        }),
        ('Response Info', {
            'fields': ('status', 'request_id', 'error_message', 'completed_at')
        }),
        ('Raw Data', {
            'classes': ('collapse',),
            'fields': ('request_payload', 'response_metadata'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
