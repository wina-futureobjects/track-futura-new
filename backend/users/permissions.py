from rest_framework import permissions

class IsSuperAdmin(permissions.BasePermission):
    """
    Custom permission to only allow superadmin users.
    """
    
    def has_permission(self, request, view):
        # Check if user is authenticated and is a superuser
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)
    
    def has_object_permission(self, request, view, obj):
        # Check if user is authenticated and is a superuser
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser) 