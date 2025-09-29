#!/usr/bin/env python
"""
Test script for Apify integration
Run this script to test the basic functionality of the Apify integration.
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apify_integration.models import ApifyConfig, ApifyBatchJob
from users.models import Project, User
from django.contrib.auth import get_user_model

def test_apify_integration():
    """Test the Apify integration functionality"""
    print("🧪 Testing Apify Integration...")
    
    # Test 1: Create a test configuration
    print("\n1. Testing configuration creation...")
    try:
        # Get API token from environment or use placeholder
        api_token = os.environ.get('APIFY_API_TOKEN', 'YOUR_APIFY_API_TOKEN')
        
        config, created = ApifyConfig.objects.get_or_create(
            platform='facebook_posts',
            defaults={
                'name': 'Test Facebook Posts',
                'api_token': api_token,
                'actor_id': 'apify/facebook-scraper',
                'description': 'Test configuration for Facebook posts',
                'is_active': True
            }
        )
        
        if created:
            print(f"✅ Created new configuration: {config.name}")
        else:
            print(f"✅ Found existing configuration: {config.name}")
            
        print(f"   Platform: {config.platform}")
        print(f"   Actor ID: {config.actor_id}")
        print(f"   Active: {config.is_active}")
        
    except Exception as e:
        print(f"❌ Error creating configuration: {str(e)}")
        return False

    # Test 2: Create a test project and batch job
    print("\n2. Testing project and batch job creation...")
    try:
        # Get or create a test user
        User = get_user_model()
        user, created = User.objects.get_or_create(
            username='test_user',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        if created:
            print(f"✅ Created test user: {user.username}")
        else:
            print(f"✅ Found existing test user: {user.username}")
        
        # Create a test project
        project, created = Project.objects.get_or_create(
            name='Test Project',
            defaults={
                'description': 'Test project for Apify integration',
                'owner': user
            }
        )
        if created:
            print(f"✅ Created test project: {project.name}")
        else:
            print(f"✅ Found existing test project: {project.name}")
        
        # Create a test batch job
        batch_job, created = ApifyBatchJob.objects.get_or_create(
            name='Test Batch Job',
            project=project,
            defaults={
                'platforms_to_scrape': ['facebook_posts'],
                'content_types_to_scrape': {'facebook_posts': ['post']},
                'num_of_posts': 10,
                'status': 'pending'
            }
        )
        
        if created:
            print(f"✅ Created test batch job: {batch_job.name}")
        else:
            print(f"✅ Found existing test batch job: {batch_job.name}")
            
        print(f"   Project: {batch_job.project.name}")
        print(f"   Platforms: {batch_job.platforms_to_scrape}")
        print(f"   Status: {batch_job.status}")
        
    except Exception as e:
        print(f"❌ Error creating project/batch job: {str(e)}")
        return False

    # Test 3: Test the Apify client (without actually running)
    print("\n3. Testing Apify client initialization...")
    try:
        from apify_client import ApifyClient
        
        client = ApifyClient(os.environ.get('APIFY_API_TOKEN', 'YOUR_APIFY_API_TOKEN'))
        
        # Test getting user info (this should work without running actors)
        user_info = client.user().get()
        print(f"✅ Apify client initialized successfully")
        print(f"   User: {user_info.get('username', 'Unknown')}")
        
    except ImportError:
        print("⚠️  Apify client not installed. Install with: pip install apify-client")
    except Exception as e:
        print(f"⚠️  Apify client test failed (expected if no valid API token): {str(e)}")

    # Test 4: Test database queries
    print("\n4. Testing database queries...")
    try:
        configs = ApifyConfig.objects.all()
        batch_jobs = ApifyBatchJob.objects.all()
        
        print(f"✅ Found {configs.count()} configurations")
        print(f"✅ Found {batch_jobs.count()} batch jobs")
        
        for config in configs[:3]:  # Show first 3
            print(f"   - {config.name} ({config.platform})")
            
    except Exception as e:
        print(f"❌ Error querying database: {str(e)}")
        return False

    print("\n🎉 Apify integration test completed successfully!")
    print("\n📝 Next steps:")
    print("   1. Set your APIFY_API_TOKEN environment variable")
    print("   2. Run: python manage.py setup_apify_configs --api-token YOUR_TOKEN")
    print("   3. Test the API endpoints at /api/apify/")
    
    return True

if __name__ == "__main__":
    success = test_apify_integration()
    sys.exit(0 if success else 1)
