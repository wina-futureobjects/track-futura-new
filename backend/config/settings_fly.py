"""
Production settings for TrackFutura project deployed on Fly.io
"""

import os
from .settings import *

# Production Security Settings
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
SECRET_KEY = os.environ.get('SECRET_KEY', "django-insecure-k14j23-+4o*h)26ms8k#ghmv*kglz!hsf^h%sac1^sy7w6f2qw")

# Hosts and Origins for Fly.io
ALLOWED_HOSTS = [
    '.fly.dev',
    'trackfutura.fly.dev',
    'localhost',
    '127.0.0.1',
]

# Parse additional allowed hosts from environment
if 'DJANGO_ALLOWED_HOSTS' in os.environ:
    additional_hosts = os.environ['DJANGO_ALLOWED_HOSTS'].split(',')
    ALLOWED_HOSTS.extend([host.strip() for host in additional_hosts])

CSRF_TRUSTED_ORIGINS = [
    'https://*.fly.dev',
    'https://trackfutura.fly.dev',
]

# Parse additional trusted origins from environment
if 'DJANGO_CSRF_TRUSTED_ORIGINS' in os.environ:
    additional_origins = os.environ['DJANGO_CSRF_TRUSTED_ORIGINS'].split(',')
    CSRF_TRUSTED_ORIGINS.extend([origin.strip() for origin in additional_origins])

# Database Configuration for Fly.io PostgreSQL
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
else:
    # Fallback to individual environment variables
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DATABASE_NAME', 'trackfutura'),
            'USER': os.environ.get('DATABASE_USER', 'postgres'),
            'PASSWORD': os.environ.get('DATABASE_PASSWORD', ''),
            'HOST': os.environ.get('DATABASE_HOST', 'localhost'),
            'PORT': os.environ.get('DATABASE_PORT', '5432'),
        }
    }

# Static Files Configuration - Serve through Django in single container
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Serve frontend static files
STATICFILES_DIRS = [
    os.path.join(BASE_DIR.parent, 'frontend', 'dist'),
]

# Media Files Configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security Settings for Production
if not DEBUG:
    SECURE_SSL_REDIRECT = os.environ.get('DJANGO_SECURE_SSL_REDIRECT', 'True').lower() == 'true'
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# CORS Configuration for production
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    f"https://{host}" for host in ALLOWED_HOSTS if not host.startswith('.') and host not in ['localhost', '127.0.0.1']
]

# Add wildcard patterns for Fly.io domains
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.fly\.dev$",
]

# BrightData Configuration
BRIGHTDATA_WEBHOOK_BASE_URL = os.environ.get(
    'BRIGHTDATA_WEBHOOK_BASE_URL',
    'https://trackfutura.fly.dev'
)

# OpenAI Configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'brightdata_integration': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Cache Configuration (using database cache for simplicity)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
    }
}

# Session Configuration
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB

# URL Configuration to serve frontend
ROOT_URLCONF = 'config.urls_fly'