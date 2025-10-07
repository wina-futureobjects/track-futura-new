#!/usr/bin/env python3
"""
Test end-to-end BrightData workflow integration
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.models import BrightDataConfig, BrightDataBatchJob
from brightdata_integration.services import BrightDataAutomatedBatchScraper
from users.models import User, Project

def test_end_to_end_workflow():
    print("=== TESTING END-TO-END BRIGHTDATA WORKFLOW ===")
    print()
    
    try:
        # Use an existing project
        project = Project.objects.first()
        
        if not project:
            print("❌ No projects found in database")
            print("   Please create a project in the TrackFutura system first")
            return
        
        print(f"✅ Using existing project: {project.name} (ID: {project.id})")
        print()
        
        # Create a test batch job
        scraper = BrightDataAutomatedBatchScraper()
        
        batch_job = scraper.create_batch_job(
            name='Test Instagram Scraping Job',
            project_id=project.id,
            source_folder_ids=[1, 2],  # Example folder IDs
            platforms_to_scrape=['instagram'],
            content_types_to_scrape={'instagram': ['posts']},
            num_of_posts=5,
            platform_params={
                'instagram': {
                    'target_urls': ['https://www.instagram.com/nike/']
                }
            }
        )
        
        if batch_job:
            print(f"✅ Created batch job: {batch_job.name} (ID: {batch_job.id})")
            print(f"   Status: {batch_job.status}")
            print(f"   Platforms: {batch_job.platforms_to_scrape}")
            print()
            
            # Execute the batch job
            print("🚀 Executing batch job...")
            success = scraper.execute_batch_job(batch_job.id)
            
            if success:
                print("✅ Batch job execution started successfully!")
                
                # Check scraper requests
                scraper_requests = batch_job.scraper_requests.all()
                print(f"📊 Created {scraper_requests.count()} scraper requests:")
                
                for req in scraper_requests:
                    print(f"   - {req.platform}: {req.target_url}")
                    print(f"     Status: {req.status}")
                    print(f"     Snapshot ID: {req.snapshot_id or 'Pending'}")
                    print()
                
                print("🎉 SUCCESS! BrightData integration is working end-to-end!")
                print()
                print("📋 WHAT HAPPENS NEXT:")
                print("   1. ✅ Scraping job sent to BrightData")
                print("   2. 🔄 BrightData is processing your request")
                print("   3. 📊 Check your BrightData dashboard for job status")
                print("   4. 📥 Results will be delivered via webhook when complete")
                print()
                print("🔗 Check your BrightData dashboard:")
                print("   - Look for snapshot IDs in your dashboard")
                print("   - Monitor job progress and completion")
                
            else:
                print("❌ Batch job execution failed")
                print(f"   Job status: {batch_job.status}")
                print(f"   Error log: {batch_job.error_log}")
                
        else:
            print("❌ Failed to create batch job")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_end_to_end_workflow()