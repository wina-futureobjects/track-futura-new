#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apify_integration.models import ApifyBatchJob, ApifyScraperRequest

# Get batch job 12
job = ApifyBatchJob.objects.get(id=12)

print(f"Batch Job ID: {job.id}")
print(f"Name: {job.name}")
print(f"Status: {job.status}")
print(f"Created: {job.created_at}")
print(f"Started: {job.started_at}")
print(f"Completed: {job.completed_at}")
print(f"\nScraper Requests:")

for req in job.scraper_requests.all():
    print(f"  Request {req.id}:")
    print(f"    Platform: {req.platform}")
    print(f"    Status: {req.status}")
    print(f"    Run ID: {req.request_id}")
    print(f"    Started: {req.started_at}")
    print(f"    Completed: {req.completed_at}")
    print(f"    Error: {req.error_message}")
    print()