#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apify_integration.models import ApifyBatchJob
from workflow.models import ScrapingJob, ScrapingRun

# Check if 32 is a batch job
try:
    batch_job = ApifyBatchJob.objects.get(id=32)
    print(f"Found ApifyBatchJob 32: {batch_job.name}, Status: {batch_job.status}")
except ApifyBatchJob.DoesNotExist:
    print("No ApifyBatchJob with ID 32")

# Check if 32 is a scraping run
try:
    scraping_run = ScrapingRun.objects.get(id=32)
    print(f"\nFound ScrapingRun 32: {scraping_run.name}, Status: {scraping_run.status}")
    print(f"Related batch jobs:")
    for job in scraping_run.scraping_jobs.all():
        print(f"  - ScrapingJob {job.id}: Batch Job {job.batch_job.id}")
except ScrapingRun.DoesNotExist:
    print("\nNo ScrapingRun with ID 32")

# Check if 32 is a scraping job
try:
    scraping_job = ScrapingJob.objects.get(id=32)
    print(f"\nFound ScrapingJob 32:")
    print(f"  Batch Job ID: {scraping_job.batch_job.id}")
    print(f"  Batch Job Name: {scraping_job.batch_job.name}")
    print(f"  Status: {scraping_job.status}")
    print(f"  Platform: {scraping_job.platform}")
except ScrapingJob.DoesNotExist:
    print("\nNo ScrapingJob with ID 32")

# List all batch jobs
print("\n\nAll Apify Batch Jobs:")
for job in ApifyBatchJob.objects.all().order_by('-id')[:10]:
    print(f"  ID {job.id}: {job.name} - {job.status}")