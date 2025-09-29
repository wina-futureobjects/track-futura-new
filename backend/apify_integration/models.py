from django.db import models
from users.models import Project
import json

class ApifyConfig(models.Model):
    PLATFORM_CHOICES = (
        ('facebook_posts', 'Facebook Posts'),
        ('facebook_reels', 'Facebook Reels'),
        ('facebook_comments', 'Facebook Comments'),
        ('instagram_posts', 'Instagram Posts'),
        ('instagram_reels', 'Instagram Reels'),
        ('instagram_comments', 'Instagram Comments'),
        ('tiktok_posts', 'TikTok Posts'),
        ('linkedin_posts', 'LinkedIn Posts'),
    )
    
    name = models.CharField(max_length=100, default="Default")
    platform = models.CharField(max_length=30, choices=PLATFORM_CHOICES, unique=True)
    api_token = models.CharField(max_length=255)
    actor_id = models.CharField(max_length=100, help_text="Apify Actor ID for this platform")
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Apify Configuration"
        verbose_name_plural = "Apify Configurations"

    def __str__(self):
        return f"{self.name} - {self.get_platform_display()} ({self.actor_id})"

class ApifyBatchJob(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )
    
    name = models.CharField(max_length=200)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='apify_batch_jobs')
    source_folder_ids = models.JSONField(default=list, blank=True)
    platforms_to_scrape = models.JSONField(default=list)
    content_types_to_scrape = models.JSONField(default=dict)
    num_of_posts = models.IntegerField(default=10)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    auto_create_folders = models.BooleanField(default=True)
    output_folder_pattern = models.CharField(max_length=200, default="platform/service/date")
    platform_params = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_sources = models.IntegerField(default=0)
    processed_sources = models.IntegerField(default=0)
    successful_requests = models.IntegerField(default=0)
    failed_requests = models.IntegerField(default=0)
    job_metadata = models.JSONField(default=dict, blank=True)
    error_log = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Apify Batch Job"
        verbose_name_plural = "Apify Batch Jobs"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.status})"

class ApifyScraperRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )
    
    config = models.ForeignKey(ApifyConfig, on_delete=models.CASCADE, related_name='scraper_requests')
    batch_job = models.ForeignKey(ApifyBatchJob, on_delete=models.CASCADE, related_name='scraper_requests')
    platform = models.CharField(max_length=50)
    content_type = models.CharField(max_length=50)
    target_url = models.URLField()
    source_name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    request_id = models.CharField(max_length=255, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Apify Scraper Request"
        verbose_name_plural = "Apify Scraper Requests"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.source_name} - {self.platform} ({self.status})"

class ApifyNotification(models.Model):
    run_id = models.CharField(max_length=255)
    status = models.CharField(max_length=50)
    message = models.TextField()
    scraper_request = models.ForeignKey(ApifyScraperRequest, on_delete=models.CASCADE, null=True, blank=True)
    raw_data = models.JSONField(default=dict)
    request_ip = models.GenericIPAddressField(null=True, blank=True)
    request_headers = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Apify Notification"
        verbose_name_plural = "Apify Notifications"
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification {self.run_id} - {self.status}"

class ApifyWebhookEvent(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    event_id = models.CharField(max_length=255, unique=True)
    run_id = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    platform = models.CharField(max_length=50, blank=True)
    raw_data = models.JSONField(default=dict)
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Apify Webhook Event"
        verbose_name_plural = "Apify Webhook Events"
        ordering = ['-created_at']

    def __str__(self):
        return f"Webhook {self.run_id} - {self.status}"
