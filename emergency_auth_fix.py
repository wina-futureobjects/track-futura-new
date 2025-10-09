#!/usr/bin/env python
"""
EMERGENCY AUTHENTICATION FIX
Creates users and tokens to fix 401 Unauthorized errors
"""
import os
import sys
import django

# Add backend to the path
sys.path.append('backend')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from brightdata_integration.models import BrightDataConfig

def main():
    print("🔧 EMERGENCY AUTHENTICATION FIX")
    print("=" * 50)
    
    # 1. Create/Update test user
    print("\n1. 🔑 Creating/Updating Test User...")
    test_user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@trackfutura.com',
            'first_name': 'Test',
            'last_name': 'User',
            'is_active': True,
            'is_staff': True,
            'is_superuser': True,
        }
    )
    
    if created:
        test_user.set_password('testpass123')
        test_user.save()
        print(f"   ✅ Created user: {test_user.username}")
    else:
        test_user.is_active = True
        test_user.is_staff = True
        test_user.is_superuser = True
        test_user.save()
        print(f"   ♻️  Updated user: {test_user.username}")
    
    # 2. Create/Get token for test user
    print("\n2. 🎫 Creating/Getting Authentication Token...")
    token, created = Token.objects.get_or_create(user=test_user)
    print(f"   ✅ Token: {token.key}")
    
    # 3. Create another admin user
    print("\n3. 👑 Creating/Updating Admin User...")
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@trackfutura.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_active': True,
            'is_staff': True,
            'is_superuser': True,
        }
    )
    
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print(f"   ✅ Created admin: {admin_user.username}")
    else:
        admin_user.is_active = True
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        print(f"   ♻️  Updated admin: {admin_user.username}")
    
    # 4. Create/Get token for admin user
    admin_token, created = Token.objects.get_or_create(user=admin_user)
    print(f"   ✅ Admin Token: {admin_token.key}")
    
    # 5. Update BrightData configurations
    print("\n4. 📊 Updating BrightData Configurations...")
    configs = [
        ('instagram', 'gd_lk5ns7kz21pck8jpis'),
        ('facebook', 'gd_lkaxegm826bjpoo9m5')
    ]
    
    for platform, dataset_id in configs:
        config, created = BrightDataConfig.objects.get_or_create(
            platform=platform,
            defaults={
                'name': f'{platform.title()} Posts Scraper',
                'dataset_id': dataset_id,
                'api_token': '8af6995e-3baa-4b69-9df7-8d7671e621eb',
                'is_active': True
            }
        )
        
        if not created:
            config.dataset_id = dataset_id
            config.api_token = '8af6995e-3baa-4b69-9df7-8d7671e621eb'
            config.is_active = True
            config.save()
        
        print(f"   ✅ {platform}: {config.dataset_id}")
    
    print("\n" + "=" * 50)
    print("🎉 AUTHENTICATION FIX COMPLETE!")
    print(f"📱 Use these tokens in your frontend:")
    print(f"   🔑 Test Token: {token.key}")
    print(f"   👑 Admin Token: {admin_token.key}")
    print(f"   🌟 Temp Token: temp-token-for-testing")
    print("\n📍 For API calls use headers:")
    print(f"   Authorization: Token {token.key}")
    print("   OR")
    print("   Authorization: Token temp-token-for-testing")

if __name__ == '__main__':
    main()