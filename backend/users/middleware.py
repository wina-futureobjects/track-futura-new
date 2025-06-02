from django.middleware.csrf import CsrfViewMiddleware, get_token
from django.urls import resolve
from django.conf import settings
from django.http import HttpResponseForbidden
import re
import logging

logger = logging.getLogger(__name__)

class CustomCsrfMiddleware(CsrfViewMiddleware):
    
    def process_view(self, request, callback, callback_args, callback_kwargs):
        # COMPLETELY DISABLE CSRF - always return None
        # This skips ALL CSRF validation for ALL requests
        return None 