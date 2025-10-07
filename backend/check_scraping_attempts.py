#!/usr/bin/env python3
"""
Check recent scraping attempts and their status
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def check_scraping_attempts():
    print("=== CHECKING RECENT SCRAPING ATTEMPTS ===")
    print()

    from brightdata_integration.models import BrightDataBatchJob, BrightDataScraperRequest
    from workflow.models import ScrapingJob, ScrapingRun

    print("1. BRIGHTDATA BATCH JOBS:")
    batch_jobs = BrightDataBatchJob.objects.all().order_by('-created_at')
    if batch_jobs.exists():
        for job in batch_jobs:
            print(f"   Job {job.id}: {job.name}")
            print(f"     Status: {job.status}")
            print(f"     Platforms: {job.platforms_to_scrape}")
            print(f"     Created: {job.created_at}")
            print(f"     Error Log: {job.error_log or 'No error log'}")
            print()
    else:
        print("   No batch jobs found")
        print()

    print("2. BRIGHTDATA SCRAPER REQUESTS:")
    requests = BrightDataScraperRequest.objects.all().order_by('-created_at')
    if requests.exists():
        for req in requests:
            print(f"   Request {req.id}: {req.platform}")
            print(f"     URL: {req.target_url}")
            print(f"     Status: {req.status}")
            print(f"     Request ID: {req.request_id or 'None'}")
            print(f"     Error: {req.error_message or 'No error'}")
            print()
    else:
        print("   No scraper requests found")
        print()

    print("3. WORKFLOW SCRAPING JOBS:")
    scraping_jobs = ScrapingJob.objects.all().order_by('-created_at')[:3]
    if scraping_jobs.exists():
        for job in scraping_jobs:
            print(f"   Workflow Job {job.id}:")
            print(f"     Status: {job.status}")
            platform_name = job.platform_service.platform.name if job.platform_service else "Unknown"
            print(f"     Platform: {platform_name}")
            print(f"     Created: {job.created_at}")
            print()
    else:
        print("   No workflow scraping jobs found")
        print()

if __name__ == "__main__":
    check_scraping_attempts()