#!/usr/bin/env python
"""
Quick script to create a test user and the exact temp token we're using for testing
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

def create_test_authentication():
    try:
        # Create or get the test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@test.com',
                'first_name': 'Test',
                'last_name': 'User',
                'is_active': True,
                'is_staff': False,
                'is_superuser': False,
            }
        )
        
        if created:
            print(f'✅ Created test user: {user.username}')
        else:
            print(f'✅ Test user already exists: {user.username}')
        
        # Delete any existing token for this user
        Token.objects.filter(user=user).delete()
        
        # Create the specific token we're using in frontend
        token = Token.objects.create(user=user, key='temp-token-for-testing')
        print(f'🔑 Created specific test token: {token.key}')
        
        # Verify token works
        test_token = Token.objects.get(key='temp-token-for-testing')
        print(f'✅ Token verification successful: User {test_token.user.username}')
        
        return True
        
    except Exception as e:
        print(f'❌ Error creating test authentication: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print('🚀 Creating test authentication...')
    success = create_test_authentication()
    if success:
        print('✅ Test authentication setup complete!')
        print('🔑 Frontend can now use token: temp-token-for-testing')
    else:
        print('❌ Test authentication setup failed!')