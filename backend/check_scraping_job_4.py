#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from workflow.models import ScrapingJob
from django.utils import timezone

# Get scraping job 4
scraping_job = ScrapingJob.objects.get(id=4)
print(f"Scraping Job 4:")
print(f"  Status: {scraping_job.status}")
print(f"  Batch Job: {scraping_job.batch_job.id} - {scraping_job.batch_job.name}")
print(f"  Batch Job Status: {scraping_job.batch_job.status}")
print(f"  Started: {scraping_job.started_at}")
print(f"  Completed: {scraping_job.completed_at}")

# Update scraping job status to match batch job status
if scraping_job.batch_job.status == 'completed' and scraping_job.status != 'completed':
    print(f"\nUpdating scraping job status to completed...")
    scraping_job.status = 'completed'
    scraping_job.completed_at = scraping_job.batch_job.completed_at or timezone.now()
    scraping_job.save()
    print(f"  Updated status: {scraping_job.status}")

# Check scraping run status after update
scraping_run = scraping_job.scraping_run
print(f"\nScraping Run {scraping_run.id}:")
print(f"  Status: {scraping_run.status}")
print(f"  Total Jobs: {scraping_run.total_jobs}")
print(f"  Completed Jobs: {scraping_run.completed_jobs}")