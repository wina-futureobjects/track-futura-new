#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apify_integration.services import ApifyAutomatedBatchScraper
from apify_integration.models import ApifyConfig, ApifyBatchJob
from users.models import Project

def test_apify_basic():
    print("🧪 Testing Apify Integration...")
    
    # Test 1: Service initialization
    scraper = ApifyAutomatedBatchScraper()
    print(f"✅ Service initialized: {scraper.base_url}")
    
    # Test 2: Check configurations
    configs = ApifyConfig.objects.filter(is_active=True)
    print(f"✅ Active configurations: {configs.count()}")
    
    # Test 3: Test connection with first config
    if configs.exists():
        config = configs.first()
        result = scraper.test_apify_connection(config)
        print(f"✅ Connection test: {result['message']}")
    
    # Test 4: Test batch job creation
    project = Project.objects.first()
    if project:
        batch_job = scraper.create_batch_job(
            name="Test API Batch Job",
            project_id=project.id,
            source_folder_ids=[1, 2],
            platforms_to_scrape=["instagram_posts"],
            content_types_to_scrape={"instagram_posts": ["post"]},
            num_of_posts=5
        )
        if batch_job:
            print(f"✅ Batch job created: {batch_job.name}")
        else:
            print("❌ Failed to create batch job")
    else:
        print("❌ No project found")
    
    # Test 5: List batch jobs
    jobs = ApifyBatchJob.objects.all()
    print(f"✅ Total batch jobs: {jobs.count()}")
    
    print("🎉 Basic Apify tests completed!")

if __name__ == "__main__":
    test_apify_basic()