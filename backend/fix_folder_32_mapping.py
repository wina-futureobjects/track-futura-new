#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from track_accounts.models import UnifiedRunFolder
from workflow.models import ScrapingJob, ScrapingRun
from apify_integration.models import ApifyBatchJob

# Get unified folder 32
unified_folder = UnifiedRunFolder.objects.get(id=32)
print(f"UnifiedRunFolder 32:")
print(f"  Name: {unified_folder.name}")
print(f"  Folder Type: {unified_folder.folder_type}")
print(f"  Platform: {unified_folder.platform_code}")
print(f"  Service: {unified_folder.service_code}")
print(f"  Parent: {unified_folder.parent_folder_id}")
print(f"  Scraping Run: {unified_folder.scraping_run_id}")

if unified_folder.scraping_run:
    scraping_run = unified_folder.scraping_run
    print(f"\n  Associated Scraping Run {scraping_run.id}:")
    print(f"    Name: {scraping_run.name}")
    print(f"    Status: {scraping_run.status}")

    # Find scraping jobs in this run
    scraping_jobs = scraping_run.scraping_jobs.all()
    print(f"    Scraping Jobs: {scraping_jobs.count()}")

    for job in scraping_jobs:
        print(f"      - Job {job.id}: Batch Job {job.batch_job.id} - {job.batch_job.name} ({job.batch_job.status})")

# Check if there are any scraping jobs with similar names
print("\n\nSearching for related batch jobs...")
batch_jobs = ApifyBatchJob.objects.filter(
    name__icontains='nike'
).order_by('-created_at')[:10]

for job in batch_jobs:
    print(f"  Batch Job {job.id}: {job.name} - {job.status} (Created: {job.created_at})")