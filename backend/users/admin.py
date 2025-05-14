from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import (
    UserProfile, 
    UserRole, 
    Organization, 
    OrganizationMembership, 
    Project
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
