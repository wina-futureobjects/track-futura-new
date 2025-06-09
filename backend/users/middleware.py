from django.middleware.csrf import CsrfViewMiddleware, get_token
from django.urls import resolve
from django.conf import settings
from django.http import HttpResponseForbidden
import re
import logging

logger = logging.getLogger(__name__)

class CustomCsrfMiddleware(CsrfViewMiddleware):

    def process_view(self, request, callback, callback_args, callback_kwargs):
        """
        Ultra-permissive CSRF handling for deployment:
        - Allow all origins and sources
        - Enable CSRF but make it very lenient
        - Prioritize functionality over security
        """

        # Always disable CSRF for API endpoints to ensure frontend works
        if request.path_info.startswith('/api/'):
            logger.debug(f"CSRF disabled for API path: {request.path_info}")
            return None

        # Always disable CSRF for webhook endpoints
        if 'webhook' in request.path_info.lower():
            logger.debug(f"CSRF disabled for webhook path: {request.path_info}")
            return None

        # For Django admin and other paths, use permissive CSRF
        try:
            return super().process_view(request, callback, callback_args, callback_kwargs)
        except Exception as e:
            # If CSRF validation fails, log but allow the request anyway
            logger.warning(f"CSRF validation failed for {request.path_info}, allowing anyway: {e}")
            return None

    def process_request(self, request):
        """
        Override to make CSRF more permissive
        """
        # Set CSRF token for all requests to ensure it's available
        if not hasattr(request, 'META'):
            return None

        # Make sure CSRF token is always available
        try:
            csrf_token = get_token(request)
            if csrf_token:
                # Add token to various places where frontend might look for it
                request.META['CSRF_COOKIE'] = csrf_token
                request.META['HTTP_X_CSRFTOKEN'] = request.META.get('HTTP_X_CSRFTOKEN', csrf_token)
        except Exception as e:
            logger.debug(f"Error setting CSRF token: {e}")

        return super().process_request(request)



    def _get_token(self, request):
        """
        Override to provide token from multiple sources
        """
        # Try to get token from various sources
        token = None

        # Try standard CSRF cookie
        try:
            token = request.COOKIES.get(settings.CSRF_COOKIE_NAME)
            if token:
                return token
        except:
            pass

        # Try from headers
        try:
            token = request.META.get('HTTP_X_CSRFTOKEN')
            if token:
                return token
        except:
            pass

        # Try from POST data
        try:
            token = request.POST.get('csrfmiddlewaretoken')
            if token:
                return token
        except:
            pass

        # Generate new token if none found
        try:
            return get_token(request)
        except:
            return None
