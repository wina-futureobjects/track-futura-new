from django.db import models

# Create your models here.

class Folder(models.Model):
    """
    Model for organizing Facebook posts into folders
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']

class FacebookPost(models.Model):
    """
    Model for storing Facebook post data
    """
    # Add folder relationship
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='posts', null=True, blank=True)
    
    # Basic fields
    url = models.URLField(max_length=500)
    post_id = models.CharField(max_length=100)
    user_url = models.URLField(max_length=500, null=True, blank=True)
    user_posted = models.CharField(max_length=100, null=True, blank=True)
    user_username_raw = models.CharField(max_length=255, null=True, blank=True)
    
    # Content fields
    content = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)  # Legacy field
    hashtags = models.TextField(null=True, blank=True)
    date_posted = models.DateTimeField(null=True, blank=True)
    
    # Engagement metrics
    num_comments = models.IntegerField(default=0)
    num_shares = models.IntegerField(null=True, blank=True)
    likes = models.IntegerField(default=0)
    video_view_count = models.IntegerField(null=True, blank=True)
    num_likes_type = models.JSONField(null=True, blank=True)
    count_reactions_type = models.JSONField(null=True, blank=True)
    
    # Page/Profile information
    page_name = models.CharField(max_length=255, null=True, blank=True)
    profile_id = models.CharField(max_length=255, null=True, blank=True)
    page_intro = models.TextField(null=True, blank=True)
    page_category = models.CharField(max_length=255, null=True, blank=True)
    page_logo = models.URLField(max_length=500, null=True, blank=True)
    page_external_website = models.URLField(max_length=500, null=True, blank=True)
    page_likes = models.IntegerField(null=True, blank=True)
    page_followers = models.IntegerField(null=True, blank=True)
    page_is_verified = models.BooleanField(default=False)
    followers = models.IntegerField(null=True, blank=True)  # Legacy field
    page_phone = models.CharField(max_length=50, null=True, blank=True)
    page_email = models.EmailField(max_length=255, null=True, blank=True)
    page_creation_time = models.DateTimeField(null=True, blank=True)
    page_reviews_score = models.CharField(max_length=20, null=True, blank=True)
    page_reviewers_amount = models.IntegerField(null=True, blank=True)
    page_price_range = models.CharField(max_length=50, null=True, blank=True)
    
    # Media content
    photos = models.TextField(null=True, blank=True)  # Legacy field
    videos = models.TextField(null=True, blank=True)  # Legacy field
    attachments_data = models.JSONField(null=True, blank=True)  # Renamed from 'attachments'
    thumbnail = models.URLField(max_length=500, null=True, blank=True)
    external_link = models.URLField(max_length=500, null=True, blank=True)
    post_image = models.URLField(max_length=500, null=True, blank=True)
    
    # External content
    post_external_link = models.URLField(max_length=500, null=True, blank=True)
    post_external_title = models.CharField(max_length=500, null=True, blank=True)
    post_external_image = models.URLField(max_length=500, null=True, blank=True)
    link_description_text = models.TextField(null=True, blank=True)
    
    # Profile images and URLs
    page_url = models.URLField(max_length=500, null=True, blank=True)
    header_image = models.URLField(max_length=500, null=True, blank=True)
    avatar_image_url = models.URLField(max_length=500, null=True, blank=True)
    profile_handle = models.CharField(max_length=255, null=True, blank=True)
    profile_image_link = models.URLField(max_length=500, null=True, blank=True)  # Legacy field
    
    # Reel specific fields
    shortcode = models.CharField(max_length=255, null=True, blank=True)
    length = models.FloatField(null=True, blank=True)
    audio = models.CharField(max_length=100, null=True, blank=True)
    
    # Metadata and flags
    is_verified = models.BooleanField(default=False)  # Legacy field
    has_handshake = models.BooleanField(default=False, null=True, blank=True)
    is_sponsored = models.BooleanField(default=False, null=True, blank=True)
    sponsor_name = models.CharField(max_length=255, null=True, blank=True)
    is_paid_partnership = models.BooleanField(default=False)
    is_page = models.BooleanField(default=False, null=True, blank=True)
    include_profile_data = models.BooleanField(default=False, null=True, blank=True)
    
    # Additional metadata
    location = models.CharField(max_length=255, null=True, blank=True)  # Legacy field
    latest_comments = models.TextField(null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    active_ads_urls = models.JSONField(null=True, blank=True)
    delegate_page_id = models.CharField(max_length=255, null=True, blank=True)
    original_post = models.JSONField(null=True, blank=True)
    other_posts_url = models.URLField(max_length=500, null=True, blank=True)
    
    # Fetch parameters
    content_type = models.CharField(max_length=50, null=True, blank=True)
    platform_type = models.CharField(max_length=50, null=True, blank=True)
    post_type = models.CharField(max_length=50, null=True, blank=True)
    days_range = models.IntegerField(null=True, blank=True)
    num_of_posts = models.IntegerField(null=True, blank=True)
    posts_count = models.IntegerField(null=True, blank=True)  # Legacy field
    posts_to_not_include = models.TextField(null=True, blank=True)
    until_date = models.DateField(null=True, blank=True)
    from_date = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    following = models.IntegerField(null=True, blank=True)
    
    # API response fields
    timestamp = models.DateTimeField(null=True, blank=True)
    input = models.JSONField(null=True, blank=True)
    error = models.TextField(null=True, blank=True)
    error_code = models.CharField(max_length=100, null=True, blank=True)
    warning = models.TextField(null=True, blank=True)
    warning_code = models.CharField(max_length=100, null=True, blank=True)
    
    # Other fields
    tagged_users = models.TextField(null=True, blank=True)
    engagement_score = models.FloatField(default=0.0)
    discovery_input = models.CharField(max_length=255, null=True, blank=True)  # Legacy field
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Post by {self.user_posted or self.page_name or 'Unknown'}"
    
    class Meta:
        ordering = ['-date_posted']
        verbose_name = "Facebook Post"
        verbose_name_plural = "Facebook Posts"
        unique_together = [['post_id', 'folder']]
        indexes = [
            models.Index(fields=['user_posted']),
            models.Index(fields=['post_id']),
            models.Index(fields=['date_posted']),
            models.Index(fields=['page_name']),
            models.Index(fields=['content_type']),
        ] 