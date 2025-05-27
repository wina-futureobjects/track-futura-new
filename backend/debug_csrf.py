#!/usr/bin/env python
"""
Debug script to check CSRF configuration in production.
Run this script to see the current CSRF and security settings.
"""

import os
import django
from django.conf import settings

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def debug_csrf_settings():
    print("=== CSRF Debug Information ===")
    print(f"DEBUG: {settings.DEBUG}")
    print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print(f"CSRF_TRUSTED_ORIGINS: {settings.CSRF_TRUSTED_ORIGINS}")
    print(f"CSRF_COOKIE_SECURE: {getattr(settings, 'CSRF_COOKIE_SECURE', 'Not set')}")
    print(f"CSRF_COOKIE_HTTPONLY: {getattr(settings, 'CSRF_COOKIE_HTTPONLY', 'Not set')}")
    print(f"CSRF_COOKIE_SAMESITE: {getattr(settings, 'CSRF_COOKIE_SAMESITE', 'Not set')}")
    print(f"SESSION_COOKIE_SECURE: {getattr(settings, 'SESSION_COOKIE_SECURE', 'Not set')}")
    print(f"CORS_ALLOW_ALL_ORIGINS: {getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', 'Not set')}")
    print(f"CORS_ALLOW_CREDENTIALS: {getattr(settings, 'CORS_ALLOW_CREDENTIALS', 'Not set')}")
    
    print("\n=== Environment Variables ===")
    platform_vars = [
        'PLATFORM_APPLICATION_NAME',
        'PLATFORM_PROJECT',
        'PLATFORM_ENVIRONMENT',
        'PLATFORM_ROUTES',
        'DJANGO_ALLOWED_HOSTS',
        'DEBUG'
    ]
    
    for var in platform_vars:
        value = os.getenv(var, 'Not set')
        if var == 'PLATFORM_ROUTES' and value != 'Not set':
            print(f"{var}: {value[:100]}..." if len(value) > 100 else f"{var}: {value}")
        else:
            print(f"{var}: {value}")
    
    print("\n=== Security Settings ===")
    security_settings = [
        'SECURE_SSL_REDIRECT',
        'SECURE_PROXY_SSL_HEADER',
        'SECURE_HSTS_SECONDS',
        'SECURE_HSTS_INCLUDE_SUBDOMAINS',
        'SECURE_HSTS_PRELOAD'
    ]
    
    for setting in security_settings:
        value = getattr(settings, setting, 'Not set')
        print(f"{setting}: {value}")

if __name__ == '__main__':
    debug_csrf_settings() 