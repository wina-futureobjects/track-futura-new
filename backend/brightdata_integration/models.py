from django.db import models
from users.models import Project

# Create your models here.

class BrightdataConfig(models.Model):
    """Model to store Brightdata API configuration with platform-specific datasets"""
    
    PLATFORM_CHOICES = (
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('tiktok', 'TikTok'),
        ('linkedin', 'LinkedIn'),
    )
    
    name = models.CharField(max_length=100, default="Default")
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default='facebook')
    api_token = models.CharField(max_length=255)
    dataset_id = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True, help_text="Description of this configuration")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Brightdata Configuration"
        verbose_name_plural = "Brightdata Configurations"
        unique_together = ['platform', 'is_active']  # Only one active config per platform

    def __str__(self):
        return f"{self.name} - {self.get_platform_display()} ({self.dataset_id})"

    def save(self, *args, **kwargs):
        # If this config is being set to active, deactivate other configs for the same platform
        if self.is_active:
            BrightdataConfig.objects.filter(platform=self.platform, is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

class BatchScraperJob(models.Model):
    """Model to store automated batch scraper jobs"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )
    
    # Job identification
    name = models.CharField(max_length=255, help_text="Name for this batch job")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='batch_scraper_jobs', null=True)
    
    # Source configuration
    source_folder_ids = models.JSONField(help_text="List of project IDs to scrape from (folders have been removed)")
    platforms_to_scrape = models.JSONField(default=list, help_text="List of platforms to scrape: ['facebook', 'instagram', 'linkedin', 'tiktok']")
    
    # Scraping parameters
    num_of_posts = models.IntegerField(default=10)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    
    # Output configuration
    auto_create_folders = models.BooleanField(default=True, help_text="Auto-create folders for results by platform and date")
    output_folder_pattern = models.CharField(max_length=255, default="{platform}_{date}_{job_name}", 
                                           help_text="Pattern for auto-created folder names")
    
    # Job status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_accounts = models.IntegerField(default=0)
    processed_accounts = models.IntegerField(default=0)
    successful_requests = models.IntegerField(default=0)
    failed_requests = models.IntegerField(default=0)
    
    # Job execution details
    job_metadata = models.JSONField(null=True, blank=True, help_text="Stores detailed job execution information")
    error_log = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Batch Scraper Job"
        verbose_name_plural = "Batch Scraper Jobs"
    
    def __str__(self):
        return f"{self.name} ({self.status})"

    def get_platforms_display(self):
        """Get a readable display of platforms to scrape"""
        if not self.platforms_to_scrape:
            return "All platforms"
        return ", ".join([p.title() for p in self.platforms_to_scrape])

class ScraperRequest(models.Model):
    """Model to store Brightdata scraper requests"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    PLATFORM_CHOICES = (
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('tiktok', 'TikTok'),
        ('linkedin', 'LinkedIn'),
    )
    
    CONTENT_TYPE_CHOICES = (
        ('post', 'Post'),
        ('reel', 'Reel'),
        ('profile', 'Profile'),
    )
    
    config = models.ForeignKey(BrightdataConfig, on_delete=models.CASCADE)
    batch_job = models.ForeignKey(BatchScraperJob, on_delete=models.CASCADE, null=True, blank=True, related_name='scraper_requests')
    
    # Request information
    request_id = models.CharField(max_length=255, blank=True, null=True)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default='post')
    target_url = models.URLField(max_length=500)
    account_name = models.CharField(max_length=255, blank=True, null=True, help_text="Name of the tracked account")
    iac_no = models.CharField(max_length=100, blank=True, null=True, help_text="IAC number of the tracked account")
    num_of_posts = models.IntegerField(default=10)
    posts_to_not_include = models.TextField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    
    # Request metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    request_payload = models.JSONField(null=True, blank=True)
    response_metadata = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    
    # Destination folder (optional, for automatic import)
    folder_id = models.IntegerField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Scraper Request"
        verbose_name_plural = "Scraper Requests"
    
    def __str__(self):
        display_name = self.account_name or self.target_url
        return f"{self.platform} - {display_name} ({self.status})"
