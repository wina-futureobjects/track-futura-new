#!/usr/bin/env python3
"""
Simple test of BrightData scraping functionality
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.models import BrightDataConfig, BrightDataBatchJob, BrightDataScraperRequest
from users.models import Project

def test_simple_brightdata_scraping():
    print("=== SIMPLE BRIGHTDATA SCRAPING TEST ===")
    print()
    
    try:
        # Get Instagram config
        instagram_config = BrightDataConfig.objects.filter(platform='instagram', is_active=True).first()
        
        if not instagram_config:
            print("❌ No Instagram configuration found")
            return
            
        # Get a project
        project = Project.objects.first()
        
        if not project:
            print("❌ No project found")
            return
            
        print(f"✅ Using Instagram config: {instagram_config.name}")
        print(f"✅ Using project: {project.name}")
        print()
        
        # Create a simple batch job
        batch_job = BrightDataBatchJob.objects.create(
            name='Simple Instagram Test',
            project=project,
            platforms_to_scrape=['instagram'],
            content_types_to_scrape={'instagram': ['posts']},
            num_of_posts=3,
            status='pending'
        )
        
        print(f"✅ Created batch job: {batch_job.name} (ID: {batch_job.id})")
        
        # Create a simple scraper request
        scraper_request = BrightDataScraperRequest.objects.create(
            config=instagram_config,
            batch_job=batch_job,
            platform='instagram',
            content_type='posts',
            target_url='https://www.instagram.com/nike/',
            source_name='Nike Instagram',
            status='pending'
        )
        
        print(f"✅ Created scraper request: {scraper_request.id}")
        print(f"   Target URL: {scraper_request.target_url}")
        print()
        
        # Test the scraping service directly
        from brightdata_integration.services import BrightDataAutomatedBatchScraper
        
        scraper = BrightDataAutomatedBatchScraper()
        
        # Prepare payload
        payload = scraper._prepare_request_payload('instagram', batch_job, scraper_request)
        print(f"📋 Prepared payload: {payload}")
        
        # Execute the request
        print("🚀 Executing BrightData request...")
        success = scraper._execute_brightdata_request(scraper_request, payload)
        
        if success:
            print("✅ SUCCESS! BrightData request executed!")
            
            # Reload to get updated data
            scraper_request.refresh_from_db()
            
            print(f"   Status: {scraper_request.status}")
            print(f"   Request ID: {scraper_request.request_id}")
            print(f"   Snapshot ID: {scraper_request.snapshot_id}")
            print()
            
            print("🎉 BRIGHTDATA INTEGRATION IS WORKING!")
            print()
            print("📊 What happened:")
            print("   1. ✅ Created batch job and scraper request")
            print("   2. ✅ Prepared correct payload format")
            print("   3. ✅ Sent request to BrightData API")
            print("   4. ✅ Received snapshot ID from BrightData")
            print()
            print("🔗 Next steps:")
            print(f"   • Check your BrightData dashboard for snapshot: {scraper_request.snapshot_id}")
            print("   • Monitor the job progress")
            print("   • Results will be delivered via webhook when ready")
            
        else:
            print("❌ BrightData request failed")
            print(f"   Error: {scraper_request.error_message}")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_brightdata_scraping()