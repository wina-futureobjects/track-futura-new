#!/usr/bin/env python
"""
Test BrightData workflow creation with restored data
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from workflow.models import Workflow, WorkflowRequest
from brightdata_integration.models import BrightDataRequest
from brightdata_integration.services import BrightDataService
from users.models import User, PlatformService

def test_brightdata_workflow():
    print("🚀 Testing BrightData workflow creation...")
    
    # Get or create a test user
    try:
        user = User.objects.get(username='superadmin')
        print(f"✅ Using user: {user.username}")
    except User.DoesNotExist:
        user = User.objects.create_user('testuser', 'test@example.com', 'testpass')
        print(f"✅ Created user: {user.username}")
    
    # Check platform services
    platform_services = PlatformService.objects.filter(
        platform__name='instagram',
        service__name='posts',
        is_enabled=True
    )
    print(f"📊 Available Instagram+Posts platform services: {platform_services.count()}")
    
    if platform_services.exists():
        ps = platform_services.first()
        print(f"✅ Using: {ps.platform.name} + {ps.service.name}")
        
        # Create workflow
        workflow = Workflow.objects.create(
            user=user,
            sources=['nike'],
            search_input='nike test search',
            platforms=['instagram'],
            services=['posts'],
            status='active'
        )
        print(f"✅ Created workflow: {workflow.id}")
        
        # Create workflow request
        workflow_request = WorkflowRequest.objects.create(
            workflow=workflow,
            platform_service=ps,
            search_query='nike instagram posts',
            status='pending'
        )
        print(f"✅ Created workflow request: {workflow_request.id}")
        
        # Test BrightData service
        brightdata_service = BrightDataService()
        
        try:
            result = brightdata_service.create_brightdata_request(
                platform='instagram',
                search_queries=['nike test'],
                workflow_request=workflow_request
            )
            print(f"✅ BrightData request created: {result}")
            
            # Check BrightData requests count
            brightdata_count = BrightDataRequest.objects.filter(
                workflow_request=workflow_request
            ).count()
            print(f"📊 BrightData requests in DB: {brightdata_count}")
            
        except Exception as e:
            print(f"❌ BrightData request failed: {e}")
            import traceback
            traceback.print_exc()
    
    else:
        print("❌ No Instagram+Posts platform service found")
    
    print("\n=== Final Status ===")
    print(f"Workflows: {Workflow.objects.count()}")
    print(f"Workflow Requests: {WorkflowRequest.objects.count()}")
    print(f"BrightData Requests: {BrightDataRequest.objects.count()}")

if __name__ == '__main__':
    test_brightdata_workflow()