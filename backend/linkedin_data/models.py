from django.db import models
from users.models import Project

# Create your models here.

class Folder(models.Model):
    """
    Model for organizing LinkedIn posts into folders
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='linkedin_folders', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']

class LinkedInPost(models.Model):
    """
    Model for storing LinkedIn post data
    """
    # Add folder relationship
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='posts', null=True, blank=True)
    
    # Existing fields
    url = models.URLField(max_length=500)
    user_posted = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    hashtags = models.TextField(null=True, blank=True)
    num_comments = models.IntegerField(default=0)
    date_posted = models.DateTimeField(null=True, blank=True)
    likes = models.IntegerField(default=0)
    photos = models.TextField(null=True, blank=True)
    videos = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    latest_comments = models.TextField(null=True, blank=True)
    post_id = models.CharField(max_length=100)
    discovery_input = models.CharField(max_length=255, null=True, blank=True)
    thumbnail = models.URLField(max_length=500, null=True, blank=True)
    content_type = models.CharField(max_length=50, null=True, blank=True)
    platform_type = models.CharField(max_length=50, null=True, blank=True)
    engagement_score = models.FloatField(default=0.0)
    tagged_users = models.TextField(null=True, blank=True)
    followers = models.IntegerField(null=True, blank=True)
    posts_count = models.IntegerField(null=True, blank=True)
    profile_image_link = models.URLField(max_length=500, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_paid_partnership = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Post by {self.user_posted}"
    
    class Meta:
        ordering = ['-date_posted']
        verbose_name = "LinkedIn Post"
        verbose_name_plural = "LinkedIn Posts"
        unique_together = [['post_id', 'folder']]
        indexes = [
            models.Index(fields=['user_posted']),
            models.Index(fields=['post_id']),
            models.Index(fields=['date_posted']),
        ] 