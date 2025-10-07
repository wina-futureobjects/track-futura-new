#!/usr/bin/env python3
"""
Simple health check endpoint for fly.io
This bypasses Django's SSL redirect for health checks
"""

import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_fly')
django.setup()

from django.http import JsonResponse
from django.db import connection


def simple_health_check():
    """Simple health check that doesn't redirect"""
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return {
            'status': 'healthy',
            'database': 'connected'
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e)
        }


if __name__ == '__main__':
    print("Health check endpoint ready")
    result = simple_health_check()
    print(result)