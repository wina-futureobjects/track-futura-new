"""
BrightData Integration Models

This module contains models for integrating with BrightData API
for social media scraping operations.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from users.models import Project


class BrightDataConfig(models.Model):
    """Configuration for BrightData integration"""
    PLATFORM_CHOICES = [
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'), 
        ('linkedin', 'LinkedIn'),
        ('tiktok', 'TikTok'),
    ]
    
    name = models.CharField(max_length=100)
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    dataset_id = models.CharField(max_length=100, help_text='BrightData dataset ID')
    api_token = models.CharField(max_length=255, help_text='BrightData API token')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['platform', 'dataset_id']
        verbose_name = "BrightData Configuration"
        verbose_name_plural = "BrightData Configurations"

    def __str__(self):
        return f"{self.name} - {self.platform}"


class BrightDataBatchJob(models.Model):
    """Represents a batch scraping job with BrightData"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=255)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='brightdata_batch_jobs')
    source_folder_ids = models.JSONField(default=list, help_text='Source folder IDs for data storage')
    platforms_to_scrape = models.JSONField(default=list, help_text='List of platforms to scrape')
    content_types_to_scrape = models.JSONField(default=dict, help_text='Content types per platform')
    platform_params = models.JSONField(default=dict, help_text='Platform-specific parameters')
    
    # Job configuration
    num_of_posts = models.IntegerField(default=10, help_text='Number of posts to scrape per source')
    start_date = models.DateField(null=True, blank=True, help_text='Start date for data collection')
    end_date = models.DateField(null=True, blank=True, help_text='End date for data collection')
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_log = models.TextField(blank=True, null=True)
    progress = models.IntegerField(default=0, help_text='Progress percentage (0-100)')
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "BrightData Batch Job"
        verbose_name_plural = "BrightData Batch Jobs"

    def __str__(self):
        return f"{self.name} - {self.status}"

    @property 
    def duration(self):
        """Calculate job duration if completed"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        elif self.started_at:
            return timezone.now() - self.started_at
        return None


class BrightDataScraperRequest(models.Model):
    """Represents individual scraper requests within a batch job"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    config = models.ForeignKey(BrightDataConfig, on_delete=models.CASCADE, related_name='scraper_requests', null=True, blank=True)
    batch_job = models.ForeignKey(BrightDataBatchJob, on_delete=models.CASCADE, related_name='scraper_requests', null=True, blank=True)
    platform = models.CharField(max_length=50)
    content_type = models.CharField(max_length=50, default='posts')
    target_url = models.CharField(max_length=500)  # Changed to CharField to allow non-URLs
    source_name = models.CharField(max_length=200, default='Unknown')
    
    # Job linking fields  
    folder_id = models.IntegerField(null=True, blank=True, help_text='Associated job folder ID (deprecated - use run_folder)')
    run_folder = models.ForeignKey('track_accounts.UnifiedRunFolder', on_delete=models.CASCADE, 
                                  related_name='scraper_requests', null=True, blank=True,
                                  help_text='Associated job folder for this scrape request')
    scrape_number = models.IntegerField(default=1, help_text='Incremental scrape number for this folder')
    user_id = models.IntegerField(null=True, blank=True, help_text='User who triggered the job')
    
    # BrightData specific fields
    request_id = models.CharField(max_length=255, blank=True, null=True, help_text='BrightData request ID')
    snapshot_id = models.CharField(max_length=255, blank=True, null=True, help_text='BrightData snapshot ID')
    dataset_id = models.CharField(max_length=255, blank=True, null=True, help_text='BrightData dataset ID')
    
    # Status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    response_data = models.JSONField(null=True, blank=True, help_text='BrightData response data')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "BrightData Scraper Request"
        verbose_name_plural = "BrightData Scraper Requests"
        indexes = [
            models.Index(fields=['folder_id', 'scrape_number'], name='bd_folder_id_scrape_idx'),
            models.Index(fields=['run_folder', 'scrape_number'], name='bd_run_folder_scrape_idx'),
        ]

    def __str__(self):
        return f"{self.platform} - {self.target_url} ({self.status})"


class BrightDataWebhookEvent(models.Model):
    """Stores webhook events from BrightData"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    event_id = models.CharField(max_length=255, unique=True)
    snapshot_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    platform = models.CharField(max_length=50, blank=True)
    raw_data = models.JSONField(default=dict)
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "BrightData Webhook Event"
        verbose_name_plural = "BrightData Webhook Events"
        ordering = ['-created_at']

    def __str__(self):
        return f"Webhook {self.snapshot_id} - {self.status}"


class BrightDataScrapedPost(models.Model):
    """Stores individual scraped posts from BrightData"""
    
    # Link to the scraper request (FIXED: Made optional for webhook processing)
    scraper_request = models.ForeignKey(BrightDataScraperRequest, on_delete=models.CASCADE, related_name='scraped_posts', null=True, blank=True)
    
    # Job/Folder linking
    folder_id = models.IntegerField(help_text='Job folder ID this post belongs to')
    
    # Post identification
    post_id = models.CharField(max_length=255, help_text='Platform-specific post ID')
    url = models.URLField(max_length=500, blank=True, null=True)
    platform = models.CharField(max_length=50, default='instagram')
    
    # Content
    user_posted = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    # Metrics
    likes = models.IntegerField(default=0)
    num_comments = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)
    
    # Metadata
    date_posted = models.DateTimeField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    hashtags = models.JSONField(default=list, blank=True)
    mentions = models.JSONField(default=list, blank=True)
    
    # Media
    media_type = models.CharField(max_length=50, blank=True, null=True)
    media_url = models.URLField(max_length=500, blank=True, null=True)
    
    # User info
    is_verified = models.BooleanField(default=False)
    follower_count = models.IntegerField(default=0)
    
    # Raw data backup
    raw_data = models.JSONField(default=dict, help_text='Original BrightData response')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['post_id', 'platform', 'scraper_request']
        verbose_name = "BrightData Scraped Post"
        verbose_name_plural = "BrightData Scraped Posts"
        ordering = ['-date_posted', '-created_at']
        indexes = [
            models.Index(fields=['folder_id']),
            models.Index(fields=['platform']),
            models.Index(fields=['user_posted']),
            models.Index(fields=['date_posted']),
        ]

    def __str__(self):
        return f"{self.platform} - {self.post_id} by {self.user_posted}"