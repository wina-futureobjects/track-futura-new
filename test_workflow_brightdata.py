#!/usr/bin/env python3
"""
Test workflow integration with BrightData
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

from workflow.services import WorkflowService
from brightdata_integration.models import BrightDataConfig
from users.models import User, Project, Platform, Service, PlatformService
from workflow.models import InputCollection

def test_workflow_brightdata_integration():
    """Test workflow integration with BrightData"""
    print("🔄 Testing Workflow + BrightData Integration...")
    
    try:
        # Get or create test data
        user = User.objects.first()
        if not user:
            print("❌ No users found in database")
            return
            
        project = Project.objects.filter(owner=user).first()
        if not project:
            project = Project.objects.create(name="Test Project", owner=user)
            
        # Get platform and service
        platform = Platform.objects.filter(name='Instagram').first()
        service = Service.objects.filter(name='Posts').first()
        
        if not platform or not service:
            print("❌ Missing platform or service data")
            return
            
        platform_service = PlatformService.objects.filter(
            platform=platform, 
            service=service
        ).first()
        
        if not platform_service:
            platform_service = PlatformService.objects.create(
                platform=platform,
                service=service,
                is_active=True
            )
            
        # Create BrightData config if not exists
        config = BrightDataConfig.objects.filter(platform='instagram').first()
        if not config:
            config = BrightDataConfig.objects.create(
                name="Instagram Posts Config",
                platform="instagram",
                dataset_id="gd_lm7t6yq9v8m8equ0r8",
                api_token="test-token-123",
                is_active=True
            )
            
        # Create input collection
        input_collection = InputCollection.objects.create(
            project=project,
            platform_service=platform_service,
            urls=["https://instagram.com/test_account"],
            status='pending'
        )
        
        print(f"✅ Created input collection: {input_collection} (ID: {input_collection.id})")
        
        # Test workflow service
        workflow_service = WorkflowService()
        
        # Test creating scraper task
        result = workflow_service.create_scraper_task(input_collection)
        
        if result:
            print(f"✅ Successfully created scraper task with BrightData integration")
        else:
            print(f"⚠️ Failed to create scraper task")
            
    except Exception as e:
        print(f"❌ Error in workflow test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_workflow_brightdata_integration()