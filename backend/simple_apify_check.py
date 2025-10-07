#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apify_integration.models import ApifyConfig, ApifyScraperRequest, ApifyBatchJob

print("=== APIFY INTEGRATION STATUS ===")
print(f"Apify Configs: {ApifyConfig.objects.count()}")
print(f"Total Scraper Requests: {ApifyScraperRequest.objects.count()}")
print(f"Active Requests: {ApifyScraperRequest.objects.filter(status__in=['pending', 'processing']).count()}")
print(f"Completed Requests: {ApifyScraperRequest.objects.filter(status='completed').count()}")
print(f"Failed Requests: {ApifyScraperRequest.objects.filter(status='failed').count()}")
print(f"Total Batch Jobs: {ApifyBatchJob.objects.count()}")

# Show recent requests
recent_requests = ApifyScraperRequest.objects.order_by('-created_at')[:5]
print("\nRecent Scraper Requests:")
for req in recent_requests:
    print(f"  - ID: {req.id}, Status: {req.status}, Request ID: {req.request_id}")

# Check if there are any test requests to clean up
test_requests = ApifyScraperRequest.objects.filter(request_id__contains='test')
if test_requests.exists():
    print(f"\nFound {test_requests.count()} test requests that can be cleaned up")