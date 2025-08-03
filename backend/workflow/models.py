from django.db import models
from django.contrib.auth.models import User

class InputCollection(models.Model):
    """Model for input collection workflow"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'), 
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ]
    
    project = models.ForeignKey('users.Project', on_delete=models.CASCADE, related_name='input_collections')
    platform_service = models.ForeignKey('users.PlatformService', on_delete=models.CASCADE, related_name='input_collections')
    urls = models.JSONField(help_text="List of URLs for scraping")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_input_collections')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Input Collection"
        verbose_name_plural = "Input Collections"
    
    def __str__(self):
        return f"{self.platform_service.platform.display_name} - {self.platform_service.service.display_name} ({self.project.name})"
    
    @property
    def platform_name(self):
        return self.platform_service.platform.display_name
    
    @property
    def service_name(self):
        return self.platform_service.service.display_name
    
    @property
    def url_count(self):
        return len(self.urls) if self.urls else 0

class WorkflowTask(models.Model):
    """Model for workflow task management"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'), 
        ('failed', 'Failed')
    ]
    
    input_collection = models.ForeignKey(InputCollection, on_delete=models.CASCADE, related_name='workflow_tasks')
    batch_job = models.ForeignKey('brightdata_integration.BatchScraperJob', on_delete=models.CASCADE, related_name='workflow_tasks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Workflow Task"
        verbose_name_plural = "Workflow Tasks"
    
    def __str__(self):
        return f"Task {self.id} - {self.input_collection} ({self.status})"
    
    @property
    def project(self):
        return self.input_collection.project
    
    @property
    def platform_service(self):
        return self.input_collection.platform_service
