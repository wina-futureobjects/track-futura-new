
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from brightdata_integration.models import BrightDataConfig, BrightDataBatchJob, BrightDataScraperRequest

print("=== BRIGHTDATA DIAGNOSIS ===")
print()

# Check BrightData configs
configs = BrightDataConfig.objects.all()
print(f"BrightData Configs: {len(configs)}")
for config in configs:
    print(f"  - {config.name} ({config.platform}): Active={config.is_active}")
    print(f"    Dataset ID: {config.dataset_id}")
    print(f"    Token: {config.api_token[:20] if config.api_token else 'None'}...")

print()

# Check recent batch jobs
recent_jobs = BrightDataBatchJob.objects.all().order_by("-created_at")[:5]
print(f"Recent Batch Jobs: {len(recent_jobs)}")
for job in recent_jobs:
    print(f"  - {job.name} ({job.status})")
    print(f"    Created: {job.created_at}")
    print(f"    Platforms: {job.platforms_to_scrape}")
    print(f"    Scraper Requests: {job.scraper_requests.count()}")
    
    # Check scraper requests for this job
    for req in job.scraper_requests.all()[:3]:  # Limit to first 3
        print(f"      * {req.platform} - {req.status}")
        if req.error_message:
            print(f"        Error: {req.error_message[:100]}")

print()

# Check if there are any pending requests without execution
pending_jobs = BrightDataBatchJob.objects.filter(status="pending")
print(f"Pending Jobs: {len(pending_jobs)}")

processing_jobs = BrightDataBatchJob.objects.filter(status="processing")
print(f"Processing Jobs: {len(processing_jobs)}")

print()
print("=== END DIAGNOSIS ===")
