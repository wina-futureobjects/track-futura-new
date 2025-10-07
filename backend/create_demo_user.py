#!/usr/bin/env python3

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

try:
    # Create demo user if it doesn't exist
    user, created = User.objects.get_or_create(
        username='demo',
        defaults={
            'email': 'demo@example.com',
            'first_name': 'Demo',
            'last_name': 'User'
        }
    )
    if created:
        user.set_password('demo123')
        user.save()
        print(f'✅ Created new user: demo')
    else:
        # Update password if user exists
        user.set_password('demo123')
        user.save()
        print(f'✅ Updated password for user: demo')

    # Create or get auth token
    token, created = Token.objects.get_or_create(user=user)
    print(f'🔑 Auth token: {token.key}')

    print('\n🎉 Demo user setup complete!')
    print(f'📋 Demo credentials:')
    print(f'   Username: demo')
    print(f'   Password: demo123')
    print(f'   Token: {token.key}')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()