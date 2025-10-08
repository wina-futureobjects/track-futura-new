"""
Custom authentication for temporary testing
"""
from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions
from django.contrib.auth.models import User


class TemporaryTestAuthentication(TokenAuthentication):
    """
    Custom authentication that accepts 'temp-token-for-testing' for bypass
    """
    
    def authenticate_credentials(self, key):
        # Accept the temp testing token
        if key == 'temp-token-for-testing':
            try:
                # Get or create a test user
                user, created = User.objects.get_or_create(
                    username='testuser',
                    defaults={
                        'email': 'test@test.com',
                        'first_name': 'Test',
                        'last_name': 'User',
                        'is_active': True,
                        'is_staff': True,
                        'is_superuser': True,
                    }
                )
                return (user, key)
            except Exception:
                # If user creation fails, just use anonymous
                pass
        
        # Fall back to normal token authentication
        return super().authenticate_credentials(key)