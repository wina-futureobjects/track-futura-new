#!/usr/bin/env python3
"""
Production Database Setup Script
Run this on the production server to create BrightData configurations and test user
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.models import BrightDataConfig
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

def create_brightdata_configs():
    """Create BrightData configurations"""
    print("Creating BrightData configurations...")
    
    # Instagram configuration
    instagram_config, created = BrightDataConfig.objects.get_or_create(
        platform='instagram',
        defaults={
            'name': 'Instagram Posts Scraper',
            'dataset_id': 'gd_lk5ns7kz21pck8jpis',
            'api_token': '8af6995e-3baa-4b69-9df7-8d7671e621eb',
            'is_active': True
        }
    )
    
    if not created:
        # Update existing config
        instagram_config.dataset_id = 'gd_lk5ns7kz21pck8jpis'
        instagram_config.api_token = '8af6995e-3baa-4b69-9df7-8d7671e621eb'
        instagram_config.is_active = True
        instagram_config.save()
    
    print(f'Instagram: {"Created" if created else "Updated"} (ID: {instagram_config.id})')
    
    # Facebook configuration
    facebook_config, created = BrightDataConfig.objects.get_or_create(
        platform='facebook',
        defaults={
            'name': 'Facebook Posts Scraper',
            'dataset_id': 'gd_lkaxegm826bjpoo9m5',
            'api_token': '8af6995e-3baa-4b69-9df7-8d7671e621eb',
            'is_active': True
        }
    )
    
    if not created:
        # Update existing config
        facebook_config.dataset_id = 'gd_lkaxegm826bjpoo9m5'
        facebook_config.api_token = '8af6995e-3baa-4b69-9df7-8d7671e621eb'
        facebook_config.is_active = True
        facebook_config.save()
    
    print(f'Facebook: {"Created" if created else "Updated"} (ID: {facebook_config.id})')
    
    return instagram_config, facebook_config

def create_test_user():
    """Create test user for authentication"""
    print("Creating test user...")
    
    user, created = User.objects.get_or_create(
        username='test',
        defaults={
            'email': 'test@trackfutura.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    
    if created:
        user.set_password('test123')
        user.save()
        print(f'Created user: {user.username}')
    else:
        # Update password anyway
        user.set_password('test123')
        user.save()
        print(f'User already exists: {user.username} (password updated)')
    
    # Create/get auth token
    token, token_created = Token.objects.get_or_create(user=user)
    print(f'Auth token: {token.key}')
    
    return user, token

def main():
    print("🚀 BRIGHTDATA PRODUCTION SETUP")
    print("=" * 50)
    
    try:
        # Create configurations
        instagram_config, facebook_config = create_brightdata_configs()
        
        # Create test user
        user, token = create_test_user()
        
        # Verify setup
        total_configs = BrightDataConfig.objects.count()
        print(f'\nTotal BrightData configs: {total_configs}')
        
        print("\n✅ Setup completed successfully!")
        print(f"✅ Instagram config ID: {instagram_config.id}")
        print(f"✅ Facebook config ID: {facebook_config.id}")
        print(f"✅ Test user: {user.username}")
        print(f"✅ Auth token: {token.key}")
        
        print("\n🎯 Next step: Test the API endpoints!")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()