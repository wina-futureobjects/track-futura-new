#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from workflow.models import ScrapingRun

# Get scraping run 8
scraping_run = ScrapingRun.objects.get(id=8)
print(f"Scraping Run 8 before update:")
print(f"  Status: {scraping_run.status}")
print(f"  Total Jobs: {scraping_run.total_jobs}")
print(f"  Completed Jobs: {scraping_run.completed_jobs}")

# Update status from jobs
scraping_run.update_status_from_jobs()

print(f"\nScraping Run 8 after update:")
print(f"  Status: {scraping_run.status}")
print(f"  Total Jobs: {scraping_run.total_jobs}")
print(f"  Completed Jobs: {scraping_run.completed_jobs}")
print(f"  Successful Jobs: {scraping_run.successful_jobs}")
print(f"  Failed Jobs: {scraping_run.failed_jobs}")