#!/usr/bin/env python3

import os
import sys

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from users.models import Organization, OrganizationMembership

try:
    # Create a test user if it doesn't exist
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f'✅ Created new user: {user.username}')
    else:
        print(f'ℹ️  User already exists: {user.username}')

    # Create or get auth token
    token, created = Token.objects.get_or_create(user=user)
    print(f'🔑 Auth token: {token.key}')

    # Create a test organization if it doesn't exist
    org, created = Organization.objects.get_or_create(
        name='Test Organization',
        defaults={
            'description': 'Test organization for development',
            'owner': user
        }
    )
    if created:
        print(f'✅ Created new organization: {org.name}')
        # Add user as admin member
        OrganizationMembership.objects.create(
            user=user,
            organization=org,
            role='admin'
        )
    else:
        print(f'ℹ️  Organization already exists: {org.name}')
        # Make sure user is a member
        membership, created = OrganizationMembership.objects.get_or_create(
            user=user,
            organization=org,
            defaults={'role': 'admin'}
        )

    print('🎉 Setup complete!')
    print(f'📋 Test credentials:')
    print(f'   Username: testuser')
    print(f'   Password: testpass123')
    print(f'   Token: {token.key}')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()