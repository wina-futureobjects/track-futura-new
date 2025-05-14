from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserRole(models.Model):
    """
    Global role for users across the entire application
    """
    ROLE_CHOICES = (
        ('super_admin', 'Super Admin'),
        ('tenant_admin', 'Tenant Admin'),
        ('user', 'User'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='global_role')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

class Organization(models.Model):
    """
    Organization model to group projects and manage user access
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # The owner of the organization
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_organizations')
    
    # Members of the organization through the membership model
    members = models.ManyToManyField(User, through='OrganizationMembership', related_name='organizations')

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']

class OrganizationMembership(models.Model):
    """
    Membership model to associate users with organizations and define their roles
    """
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('member', 'Member'),
        ('viewer', 'Viewer'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    date_joined = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'organization')
        
    def __str__(self):
        return f"{self.user.username} - {self.organization.name} ({self.role})"

class Project(models.Model):
    """
    Model for organizing data into separate projects
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    # Change from direct user ownership to organization ownership
    # Make it nullable initially to allow for migration
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='projects', null=True, blank=True)
    
    # Keep the owner field for tracking who created the project
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    
    # Access control
    is_public = models.BooleanField(default=False, help_text="If true, all organization members can access")
    
    # M2M relationship for specific users who have access (in addition to admins and owner)
    authorized_users = models.ManyToManyField(User, related_name='accessible_projects', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']
