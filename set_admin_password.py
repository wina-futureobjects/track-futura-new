#!/usr/bin/env python
"""
Quick script to set admin password for Django admin access
"""
import os
import django
import sys

# Add the backend directory to the Python path
sys.path.insert(0, '/app/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trackfutura.settings')
django.setup()

from django.contrib.auth.models import User

try:
    # Get or create superadmin user
    user, created = User.objects.get_or_create(
        username='superadmin',
        defaults={
            'email': 'admin@trackfutura.com',
            'is_staff': True,
            'is_superuser': True,
            'is_active': True
        }
    )
    
    # Set a simple password
    user.set_password('admin123')
    user.save()
    
    print("✅ Admin password set successfully!")
    print(f"Username: superadmin")
    print(f"Password: admin123")
    print(f"Login at: https://trackfutura.futureobjects.io/admin/")
    print(f"BrightData data: https://trackfutura.futureobjects.io/admin/brightdata_integration/brightdatawebhookevent/")
    
except Exception as e:
    print(f"❌ Error: {e}")