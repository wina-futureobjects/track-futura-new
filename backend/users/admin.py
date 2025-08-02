from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import (
    UserProfile, 
    UserRole, 
    Organization, 
    OrganizationMembership, 
    Project,
    Platform,
    Service,
    PlatformService
)

# UserRole Admin
@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'created_at', 'updated_at')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email')
    ordering = ('user__username',)
    raw_id_fields = ('user',)

# UserProfile Admin
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'avatar', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email')
    raw_id_fields = ('user',)

# Organization Admin
@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'get_member_count', 'created_at', 'updated_at')
    search_fields = ('name', 'owner__username', 'description')
    list_filter = ('created_at',)
    raw_id_fields = ('owner',)
    
    def get_member_count(self, obj):
        return obj.members.count()
    get_member_count.short_description = 'Members'

# OrganizationMembership Admin
@admin.register(OrganizationMembership)
class OrganizationMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'role', 'date_joined')
    list_filter = ('role', 'date_joined')
    search_fields = ('user__username', 'organization__name')
    raw_id_fields = ('user', 'organization')

# Project Admin
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'owner', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('name', 'description', 'owner__username')
    raw_id_fields = ('owner', 'organization')
    filter_horizontal = ('authorized_users',)

# Extend the User admin
class UserRoleInline(admin.StackedInline):
    model = UserRole
    can_delete = False
    verbose_name_plural = 'User Role'

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserRoleInline, UserProfileInline,)
    list_display = BaseUserAdmin.list_display + ('get_role',)
    
    def get_role(self, obj):
        try:
            return obj.global_role.get_role_display()
        except UserRole.DoesNotExist:
            return "-"
    get_role.short_description = 'Role'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'name', 'is_enabled', 'created_by', 'created_at']
    list_filter = ['is_enabled', 'created_at']
    search_fields = ['name', 'display_name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['display_name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'display_name', 'description')
        }),
        ('UI Configuration', {
            'fields': ('icon_name', 'color')
        }),
        ('Status', {
            'fields': ('is_enabled',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'name', 'icon_name', 'created_at']
    search_fields = ['name', 'display_name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['display_name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'display_name', 'description')
        }),
        ('UI Configuration', {
            'fields': ('icon_name',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(PlatformService)
class PlatformServiceAdmin(admin.ModelAdmin):
    list_display = ['platform', 'service', 'is_enabled', 'is_available', 'created_by', 'created_at']
    list_filter = ['is_enabled', 'platform', 'service', 'created_at']
    search_fields = ['platform__name', 'platform__display_name', 'service__name', 'service__display_name']
    readonly_fields = ['created_at', 'updated_at', 'is_available']
    ordering = ['platform__display_name', 'service__display_name']
    
    fieldsets = (
        ('Platform Service Configuration', {
            'fields': ('platform', 'service', 'is_enabled', 'description')
        }),
        ('Status', {
            'fields': ('is_available',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_available(self, obj):
        return obj.is_available
    is_available.boolean = True
    is_available.short_description = 'Available'
