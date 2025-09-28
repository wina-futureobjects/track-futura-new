"""
Production settings for TrackFutura project deployed on Upsun
"""

import os
import json
from .settings import *

# Parse the Upsun relationships from environment
relationships = {}
if 'PLATFORM_RELATIONSHIPS' in os.environ:
    relationships = json.loads(os.environ['PLATFORM_RELATIONSHIPS'])

# Production Security Settings
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
SECRET_KEY = os.environ.get('SECRET_KEY', "django-insecure-k14j23-+4o*h)26ms8k#ghmv*kglz!hsf^h%sac1^sy7w6f2qw")

# Hosts and Origins
ALLOWED_HOSTS = [
    '.upsun.app',
    '.platform.sh',
    'localhost',
    '127.0.0.1',
]

# Parse additional allowed hosts from environment
if 'DJANGO_ALLOWED_HOSTS' in os.environ:
    additional_hosts = os.environ['DJANGO_ALLOWED_HOSTS'].split(',')
    ALLOWED_HOSTS.extend([host.strip() for host in additional_hosts])

CSRF_TRUSTED_ORIGINS = [
    'https://*.upsun.app',
    'https://*.platform.sh',
]

# Parse additional trusted origins from environment
if 'DJANGO_CSRF_TRUSTED_ORIGINS' in os.environ:
    additional_origins = os.environ['DJANGO_CSRF_TRUSTED_ORIGINS'].split(',')
    CSRF_TRUSTED_ORIGINS.extend([origin.strip() for origin in additional_origins])

# Database Configuration for Upsun
if relationships and 'database' in relationships:
    db_config = relationships['database'][0]
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': db_config['path'],
            'USER': db_config['username'],
            'PASSWORD': db_config['password'],
            'HOST': db_config['host'],
            'PORT': db_config['port'],
            'OPTIONS': {
                'sslmode': 'require',
            },
        }
    }
else:
    # Fallback to environment variables for database configuration
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

# Static Files Configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

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
    f"https://{host}" for host in ALLOWED_HOSTS if not host.startswith('.')
]

# Add wildcard patterns for Upsun domains
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.upsun\.app$",
    r"^https://.*\.platform\.sh$",
]

# BrightData Configuration
BRIGHTDATA_WEBHOOK_BASE_URL = os.environ.get(
    'BRIGHTDATA_WEBHOOK_BASE_URL',
    'https://api.{default}'
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

# Email Configuration (for error reporting)
if 'EMAIL_HOST' in os.environ:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('EMAIL_HOST')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@trackfutura.app')

# Session Configuration
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB