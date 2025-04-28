from django.db import models
import json

# Create your models here.

class TrackAccountFolder(models.Model):
    """
    Model for organizing Track Accounts into folders
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Track Account Folder"
        verbose_name_plural = "Track Account Folders"

class TrackAccount(models.Model):
    """
    Model for storing Track Account data
    """
    # Add folder relationship
    folder = models.ForeignKey(TrackAccountFolder, on_delete=models.CASCADE, related_name='accounts', null=True, blank=True)
    
    # Fields from the CSV
    name = models.CharField(max_length=255)
    iac_no = models.CharField(max_length=100, unique=True)
    
    # Social media usernames (from FB, IG, LK, TK columns)
    facebook_username = models.CharField(max_length=100, blank=True, null=True)
    instagram_username = models.CharField(max_length=100, blank=True, null=True)
    linkedin_username = models.CharField(max_length=100, blank=True, null=True)
    tiktok_username = models.CharField(max_length=100, blank=True, null=True)
    
    # Social media profile URLs (from FACEBOOK_ID, INSTAGRAM_ID, etc columns)
    facebook_id = models.URLField(max_length=500, blank=True, null=True)
    instagram_id = models.URLField(max_length=500, blank=True, null=True)
    linkedin_id = models.URLField(max_length=500, blank=True, null=True)
    tiktok_id = models.URLField(max_length=500, blank=True, null=True)
    
    other_social_media = models.TextField(blank=True, null=True)
    risk_classification = models.CharField(max_length=100, blank=True, null=True)
    close_monitoring = models.BooleanField(default=False)
    posting_frequency = models.CharField(max_length=100, blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.iac_no})"
    
    class Meta:
        ordering = ['name']
        verbose_name = "Track Account"
        verbose_name_plural = "Track Accounts"
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['iac_no']),
            models.Index(fields=['risk_classification']),
        ]

class ReportFolder(models.Model):
    """
    Model for storing generated reports
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    source_folders = models.TextField(blank=True, null=True)  # JSON array of folder IDs used for this report
    
    # Statistics
    total_posts = models.IntegerField(default=0)
    matched_posts = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def get_source_folders(self):
        """Get source folder IDs as a list"""
        if not self.source_folders:
            return []
        try:
            return json.loads(self.source_folders)
        except json.JSONDecodeError:
            return []
    
    def set_source_folders(self, folder_ids):
        """Store source folder IDs as JSON string"""
        self.source_folders = json.dumps(folder_ids)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Report Folder"
        verbose_name_plural = "Report Folders"

class ReportEntry(models.Model):
    """
    Model for individual report entries (rows in the report)
    """
    report = models.ForeignKey(ReportFolder, on_delete=models.CASCADE, related_name='entries')
    
    # Data from the report row
    sn = models.CharField(max_length=50, blank=True, null=True)  # S/N field, can be left empty
    name = models.CharField(max_length=255, blank=True, null=True)
    iac_no = models.CharField(max_length=100, blank=True, null=True)
    entity = models.CharField(max_length=255, blank=True, null=True)
    close_monitoring = models.CharField(max_length=5, blank=True, null=True)  # "Yes" or "No"
    posting_date = models.DateTimeField(blank=True, null=True)
    platform_type = models.CharField(max_length=50, blank=True, null=True)
    post_url = models.URLField(max_length=500, blank=True, null=True)
    username = models.CharField(max_length=100, blank=True, null=True)
    account_type = models.CharField(max_length=100, blank=True, null=True)  # Personal/Business
    keywords = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    
    # Original post ID for reference
    post_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Track Account ID for reference (if matched)
    track_account_id = models.IntegerField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Report entry for {self.name or self.username or 'Unknown'}"
    
    class Meta:
        ordering = ['-posting_date']
        verbose_name = "Report Entry"
        verbose_name_plural = "Report Entries"
