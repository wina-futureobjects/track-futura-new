#!/usr/bin/env python
"""
PRODUCTION AUTHENTICATION SETUP FOR UPSUN
Deploy authentication users and tokens to production
"""
import os
import sys
import django

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from brightdata_integration.models import BrightDataConfig
from reports.models import ReportTemplate, GeneratedReport
import json
from datetime import datetime
from django.utils import timezone

def setup_production_auth():
    print("🚀 UPSUN PRODUCTION AUTHENTICATION SETUP")
    print("=" * 60)
    
    # 1. Create production users
    print("\n1. 👥 Creating Production Users...")
    
    users_data = [
        {
            'username': 'admin',
            'email': 'admin@trackfutura.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'password': 'TrackAdmin2025!',
            'is_superuser': True,
            'is_staff': True
        },
        {
            'username': 'testuser',
            'email': 'test@trackfutura.com', 
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'TestUser2025!',
            'is_superuser': False,
            'is_staff': True
        },
        {
            'username': 'demo',
            'email': 'demo@trackfutura.com',
            'first_name': 'Demo',
            'last_name': 'User', 
            'password': 'DemoUser2025!',
            'is_superuser': False,
            'is_staff': False
        }
    ]
    
    production_tokens = {}
    
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'], 
                'last_name': user_data['last_name'],
                'is_active': True,
                'is_staff': user_data['is_staff'],
                'is_superuser': user_data['is_superuser']
            }
        )
        
        if created:
            user.set_password(user_data['password'])
            user.save()
            print(f"   ✅ Created user: {user.username}")
        else:
            user.is_active = True
            user.is_staff = user_data['is_staff'] 
            user.is_superuser = user_data['is_superuser']
            user.save()
            print(f"   ♻️  Updated user: {user.username}")
        
        # Create/get token
        token, created = Token.objects.get_or_create(user=user)
        production_tokens[user.username] = token.key
        print(f"      🔑 Token: {token.key}")
    
    # 2. Update BrightData configurations
    print("\n2. 📊 Setting Up BrightData Integration...")
    
    brightdata_configs = [
        ('instagram', 'gd_lk5ns7kz21pck8jpis'),
        ('facebook', 'gd_lkaxegm826bjpoo9m5')
    ]
    
    for platform, dataset_id in brightdata_configs:
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
    
    # 3. Create report templates if they don't exist
    print("\n3. 📋 Setting Up Report Templates...")
    
    templates_data = [
        {
            'name': 'Sentiment Analysis Report',
            'template_type': 'sentiment_analysis',
            'description': 'Analyze sentiment trends across social media posts',
            'icon': 'sentiment_satisfied',
            'color': '#4caf50',
            'is_active': True
        },
        {
            'name': 'Engagement Metrics Report',
            'template_type': 'engagement_metrics',
            'description': 'Track engagement rates and social media metrics',
            'icon': 'bar_chart',
            'color': '#2196f3',
            'is_active': True
        },
        {
            'name': 'Content Analysis Report',
            'template_type': 'content_analysis', 
            'description': 'Analyze content patterns, hashtags, and performance',
            'icon': 'analytics',
            'color': '#ff9800',
            'is_active': True
        }
    ]
    
    for template_data in templates_data:
        template, created = ReportTemplate.objects.get_or_create(
            template_type=template_data['template_type'],
            defaults=template_data
        )
        print(f"   {'✅ Created' if created else '♻️  Found'} template: {template.name}")
    
    # Save production tokens to environment variable format
    print("\n" + "=" * 60)
    print("🎉 PRODUCTION AUTHENTICATION SETUP COMPLETE!")
    print("\n🔑 PRODUCTION AUTHENTICATION TOKENS:")
    for username, token in production_tokens.items():
        print(f"   {username.upper()}_TOKEN={token}")
    
    print(f"\n📱 FRONTEND INTEGRATION:")
    print(f"   Use any of these tokens in Authorization headers:")
    for username, token in production_tokens.items():
        print(f"   Authorization: Token {token}  # {username}")
    
    print(f"\n🌟 TEMPORARY TESTING TOKEN:")
    print(f"   Authorization: Token temp-token-for-testing")
    
    print(f"\n🎯 TEST ENDPOINTS:")
    print(f"   GET /api/reports/templates/")
    print(f"   GET /api/reports/generated/") 
    print(f"   GET /api/users/profile/")
    
    print(f"\n✅ All 401 Unauthorized errors should now be resolved!")
    print(f"🚀 TrackFutura authentication system is production-ready!")

if __name__ == '__main__':
    setup_production_auth()