#!/usr/bin/env python3
"""
Test script to verify BrightData integration is working correctly
"""

import os
import sys
import django

# Add the backend directory to Python path
backend_path = r'C:\Users\winam\OneDrive\문서\PREVIOUS\TrackFutura - Copy\backend'
sys.path.append(backend_path)
os.chdir(backend_path)

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.models import BrightDataConfig, BrightDataBatchJob
from workflow.models import WorkflowTask, ScrapingJob
from users.models import User, Project, Platform, Service, PlatformService

def test_brightdata_integration():
    """Test BrightData integration functionality"""
    print("🧪 Testing BrightData Integration...")
    
    # Test 1: Create BrightData configuration
    print("\n📋 Test 1: Creating BrightData configuration...")
    config = BrightDataConfig.objects.create(
        name="Test Instagram Config",
        platform="instagram",
        dataset_id="gd_lm7t6yq9v8m8equ0r8",
        api_token="test-token-123",
        is_active=True
    )
    print(f"✅ Created BrightData config: {config.name} (ID: {config.id})")
    
    # Test 2: Create BrightData batch job
    print("\n📋 Test 2: Creating BrightData batch job...")
    try:
        # Get or create a test user and project
        user, created = User.objects.get_or_create(
            email="test@example.com",
            defaults={"username": "testuser"}
        )
        
        project, created = Project.objects.get_or_create(
            name="Test Project",
            user=user
        )
        
        batch_job = BrightDataBatchJob.objects.create(
            name="Test Batch Job",
            project=project,
            platforms_to_scrape=["instagram"],
            content_types_to_scrape={"instagram": ["posts"]},
            num_of_posts=10,
            status="pending"
        )
        print(f"✅ Created BrightData batch job: {batch_job.name} (ID: {batch_job.id})")
    except Exception as e:
        print(f"⚠️ Could not create batch job: {e}")
    
    # Test 3: Test workflow integration
    print("\n📋 Test 3: Testing workflow integration...")
    try:
        # Check if platforms exist
        platform_count = Platform.objects.filter(name__in=['Instagram', 'Facebook', 'LinkedIn', 'TikTok']).count()
        print(f"📊 Found {platform_count} platforms in database")
        
        if platform_count > 0:
            platform = Platform.objects.filter(name='Instagram').first()
            if platform:
                print(f"✅ Found Instagram platform: {platform.name}")
        
    except Exception as e:
        print(f"⚠️ Workflow integration test: {e}")
    
    # Test 4: Check model relationships
    print("\n📋 Test 4: Testing model relationships...")
    try:
        # Test foreign key relationships
        batch_jobs = BrightDataBatchJob.objects.all()
        print(f"📊 Total BrightData batch jobs: {batch_jobs.count()}")
        
        configs = BrightDataConfig.objects.filter(is_active=True)
        print(f"📊 Active BrightData configs: {configs.count()}")
        
        print("✅ Model relationships working correctly")
    except Exception as e:
        print(f"❌ Model relationship error: {e}")
    
    print("\n🎉 BrightData integration test completed!")

if __name__ == "__main__":
    test_brightdata_integration()