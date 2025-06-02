from django.middleware.csrf import CsrfViewMiddleware, get_token
from django.urls import resolve
from django.conf import settings
from django.http import HttpResponseForbidden
import re
import logging

logger = logging.getLogger(__name__)

class CustomCsrfMiddleware(CsrfViewMiddleware):
    
    def _get_failure_view(self):
        """Return a custom CSRF failure response with debugging info"""
        return self._reject
    
    def _reject(self, request, reason):
        """Custom rejection with debugging"""
        if settings.DEBUG:
            logger.warning(f"CSRF Rejection: {reason}")
            logger.warning(f"Request Origin: {request.META.get('HTTP_ORIGIN', 'None')}")
            logger.warning(f"Request Referer: {request.META.get('HTTP_REFERER', 'None')}")
            logger.warning(f"CSRF Trusted Origins: {getattr(settings, 'CSRF_TRUSTED_ORIGINS', [])}")
        
        return HttpResponseForbidden(f"CSRF verification failed. {reason}")
    
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
            r'^admin/login/$',  # Django admin login
            r'^api/.*/$',  # All API endpoints in production
        ]
        
        # In production (Upsun), be more permissive with API endpoints
        if hasattr(settings, 'PLATFORM_APPLICATION_NAME') or not settings.DEBUG:
            exempt_paths.extend([
                r'^api/.*',  # All API endpoints
                r'^admin/.*',  # All admin endpoints
            ])
        
        # If the path matches any of the exempt paths, skip CSRF validation
        for exempt_path in exempt_paths:
            if re.match(exempt_path, path):
                if settings.DEBUG:
                    logger.info(f"CSRF exempted for path: {path}")
                return None  # Skip CSRF validation
        
        # Otherwise, proceed with CSRF validation
        return super().process_view(request, callback, callback_args, callback_kwargs) 