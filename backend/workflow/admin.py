from django.contrib import admin
from .models import InputCollection, WorkflowTask

@admin.register(InputCollection)
class InputCollectionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'project', 'platform_name', 'service_name', 
        'url_count', 'status', 'created_by', 'created_at'
    ]
    list_filter = ['status', 'created_at', 'platform_service__platform', 'platform_service__service']
    search_fields = ['project__name', 'platform_service__platform__display_name', 'platform_service__service__display_name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'platform_name', 'service_name', 'url_count']
    date_hierarchy = 'created_at'
    
    def platform_name(self, obj):
        return obj.platform_name
    platform_name.short_description = 'Platform'
    
    def service_name(self, obj):
        return obj.service_name
    service_name.short_description = 'Service'
    
    def url_count(self, obj):
        return obj.url_count
    url_count.short_description = 'URL Count'

@admin.register(WorkflowTask)
class WorkflowTaskAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'input_collection', 'batch_job', 'status', 'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['input_collection__project__name', 'batch_job__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
