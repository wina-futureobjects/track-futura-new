from django.contrib import admin
from .models import BrightDataConfig, BrightDataBatchJob, BrightDataScraperRequest, BrightDataWebhookEvent, BrightDataScrapedPost


@admin.register(BrightDataConfig)
class BrightDataConfigAdmin(admin.ModelAdmin):
    list_display = ['name', 'platform', 'dataset_id', 'is_active', 'created_at']
    list_filter = ['platform', 'is_active', 'created_at']
    search_fields = ['name', 'platform', 'dataset_id']
    ordering = ['-created_at']


@admin.register(BrightDataBatchJob)
class BrightDataBatchJobAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'status', 'progress', 'num_of_posts', 'created_at']
    list_filter = ['status', 'created_at', 'project']
    search_fields = ['name', 'project__name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'started_at', 'completed_at']


@admin.register(BrightDataScraperRequest)
class BrightDataScraperRequestAdmin(admin.ModelAdmin):
    list_display = ['platform', 'target_url', 'status', 'batch_job', 'created_at']
    list_filter = ['platform', 'status', 'created_at']
    search_fields = ['target_url', 'platform', 'request_id', 'snapshot_id']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'started_at', 'completed_at']


@admin.register(BrightDataWebhookEvent)
class BrightDataWebhookEventAdmin(admin.ModelAdmin):
    list_display = ['event_id', 'snapshot_id', 'platform', 'status', 'created_at']
    list_filter = ['platform', 'status', 'created_at']
    search_fields = ['event_id', 'snapshot_id', 'platform']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'processed_at']


@admin.register(BrightDataScrapedPost)
class BrightDataScrapedPostAdmin(admin.ModelAdmin):
    list_display = ['post_id', 'platform', 'folder_id', 'likes', 'num_comments', 'created_at']
    list_filter = ['platform', 'folder_id', 'created_at']
    search_fields = ['post_id', 'content', 'user_posted', 'platform']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']