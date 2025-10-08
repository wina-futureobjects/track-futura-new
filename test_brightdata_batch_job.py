#!/usr/bin/env python
"""
Test BrightData batch job creation with restored platform services
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.services import BrightDataAutomatedBatchScraper
from brightdata_integration.models import BrightDataConfig, BrightDataBatchJob
from users.models import PlatformService, User, Project

def test_brightdata_batch_job():
    print("🚀 Testing BrightData batch job creation...")
    
    # Check platform services
    instagram_posts = PlatformService.objects.filter(
        platform__name='instagram',
        service__name='posts',
        is_enabled=True
    ).first()
    
    if instagram_posts:
        print(f"✅ Found platform service: {instagram_posts.platform.name} + {instagram_posts.service.name}")
        
        # Get or create a test project
        user = User.objects.first()
        if not user:
            print("❌ No users found")
            return
            
        project, created = Project.objects.get_or_create(
            name='Test BrightData Project',
            defaults={'owner': user}
        )
        print(f"✅ Project: {project.name} (created: {created})")
        
        # Check BrightData config
        config = BrightDataConfig.objects.filter(platform='instagram', is_active=True).first()
        if config:
            print(f"✅ Found BrightData config: {config.platform} -> {config.dataset_id}")
            
            # Test batch job creation
            service = BrightDataAutomatedBatchScraper()
            
            try:
                batch_job = service.create_batch_job(
                    name="Test BrightData Job",
                    project_id=project.id,
                    source_folder_ids=[1],  # Test folder ID
                    platforms_to_scrape=['instagram'],
                    content_types_to_scrape={'instagram': ['posts']},
                    num_of_posts=5
                )
                
                if batch_job:
                    print(f"✅ Batch job created: {batch_job.id} - {batch_job.name}")
                    print(f"   Status: {batch_job.status}")
                    print(f"   Platforms: {batch_job.platforms_to_scrape}")
                else:
                    print("❌ Batch job creation returned None")
                
            except Exception as e:
                print(f"❌ Batch job creation failed: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("❌ No BrightData config found for Instagram")
    else:
        print("❌ No Instagram+Posts platform service found")
    
    print("\n=== Final Status ===")
    print(f"Platform Services: {PlatformService.objects.count()}")
    print(f"BrightData Configs: {BrightDataConfig.objects.count()}")
    print(f"BrightData Batch Jobs: {BrightDataBatchJob.objects.count()}")

if __name__ == '__main__':
    test_brightdata_batch_job()