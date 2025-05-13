from django.db import models

# Create your models here.

class BrightdataConfig(models.Model):
    """Model to store Brightdata API configuration"""
    name = models.CharField(max_length=100, default="Default")
    api_token = models.CharField(max_length=255)
    dataset_id = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Brightdata Configuration"
        verbose_name_plural = "Brightdata Configurations"

    def __str__(self):
        return f"{self.name} ({self.dataset_id})"

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
    
    # Request information
    request_id = models.CharField(max_length=255, blank=True, null=True)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default='post')
    target_url = models.URLField(max_length=500)
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
        return f"{self.platform} - {self.target_url} ({self.status})"
