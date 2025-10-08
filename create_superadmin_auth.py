#!/usr/bin/env python
"""
Create superadmin user and tokens for authentication
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

def create_superadmin():
    try:
        # Create or get the superadmin user
        user, created = User.objects.get_or_create(
            username='superadmin',
            defaults={
                'email': 'admin@trackfutura.com',
                'first_name': 'Super',
                'last_name': 'Admin',
                'is_active': True,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        
        # Set password
        user.set_password('admin123')
        user.save()
        
        if created:
            print(f'✅ Created superadmin user: {user.username}')
        else:
            print(f'✅ Updated superadmin user: {user.username}')
        
        # Delete any existing token for this user
        Token.objects.filter(user=user).delete()
        
        # Create a real token
        token = Token.objects.create(user=user)
        print(f'🔑 Created superadmin token: {token.key}')
        
        # Also create the specific test token for easier testing
        test_user, test_created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@test.com',
                'first_name': 'Test',
                'last_name': 'User',
                'is_active': True,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        
        # Delete any existing token for test user
        Token.objects.filter(user=test_user).delete()
        
        # Create the specific token we're using in frontend
        test_token = Token.objects.create(user=test_user, key='temp-token-for-testing')
        print(f'🔑 Created test token: {test_token.key}')
        
        print('✅ Authentication setup complete!')
        print(f'🚀 You can now login with:')
        print(f'   Username: superadmin')
        print(f'   Password: admin123')
        print(f'   Token: {token.key}')
        print(f'🧪 Or use temp-token-for-testing for automated testing')
        
        return True
        
    except Exception as e:
        print(f'❌ Error creating authentication: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print('🚀 Creating superadmin authentication...')
    success = create_superadmin()
    if not success:
        sys.exit(1)