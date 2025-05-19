from django.middleware.csrf import CsrfViewMiddleware, get_token
from django.urls import resolve
from django.conf import settings
import re

class CustomCsrfMiddleware(CsrfViewMiddleware):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        # Always ensure CSRF cookie is set by getting the token
        # This forces the cookie to be set for future requests
        get_token(request)
        
        # Check if the path is exempt from CSRF
        path = request.path_info.lstrip('/')
        
        # Define paths to exempt from CSRF protection
        exempt_paths = [
            r'^api/users/login/$',  # Login endpoint
            r'^api/users/register/$',  # Registration endpoint
        ]
        
        # If the path matches any of the exempt paths, skip CSRF validation
        for exempt_path in exempt_paths:
            if re.match(exempt_path, path):
                return None  # Skip CSRF validation
        
        # Otherwise, proceed with CSRF validation
        return super().process_view(request, callback, callback_args, callback_kwargs) 