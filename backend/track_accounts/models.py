from django.db import models
import json
from users.models import Project

# Create your models here.

class TrackSource(models.Model):
    """
    Model for storing Track Source data (formerly Track Account)
    """
    # Reference to the project
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='track_sources', null=True)
    
    # Fields from the CSV
    name = models.CharField(max_length=255)
    iac_no = models.CharField(max_length=100, unique=True)
    
    # Social media profile URLs (renamed from _id to _link for clarity)
    facebook_link = models.URLField(max_length=500, blank=True, null=True)
    instagram_link = models.URLField(max_length=500, blank=True, null=True)
    linkedin_link = models.URLField(max_length=500, blank=True, null=True)
    tiktok_link = models.URLField(max_length=500, blank=True, null=True)
    
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
        verbose_name = "Track Source"
        verbose_name_plural = "Track Sources"
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['iac_no']),
            models.Index(fields=['risk_classification']),
        ]

# Keep backward compatibility alias
TrackAccount = TrackSource

class ReportFolder(models.Model):
    """
    Model for storing generated reports
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='report_folders', null=True)
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
    
    # Track Source ID for reference (if matched) - updated from track_account_id
    track_source_id = models.IntegerField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Report entry for {self.name or self.username or 'Unknown'}"
    
    class Meta:
        ordering = ['-posting_date']
        verbose_name = "Report Entry"
        verbose_name_plural = "Report Entries"
