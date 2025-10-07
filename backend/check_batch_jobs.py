#!/usr/bin/env python3

import os
import sys

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

# Check batch jobs
from apify_integration.models import ApifyBatchJob

print("Batch Jobs in database:")
jobs = ApifyBatchJob.objects.all()
for job in jobs:
    print(f"ID: {job.id}, Name: {job.name}, Status: {job.status}, Platforms: {job.platforms_to_scrape}")

print(f"\nTotal jobs: {jobs.count()}")

# Also check if ViewSet is working
from apify_integration.views import ApifyBatchJobViewSet
print("\nViewSet imported successfully!")

# Test the API endpoint manually
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser

factory = RequestFactory()
view = ApifyBatchJobViewSet()

# Try to get job 8
try:
    request = factory.get('/api/apify/batch-jobs/8/')
    request.user = AnonymousUser()
    view.setup(request)
    
    # Simulate the retrieve method
    job = ApifyBatchJob.objects.filter(id=8).first()
    if job:
        print(f"\nJob 8 found in database: {job.name}")
    else:
        print("\nJob 8 NOT found in database")
        
    # Check what jobs exist
    all_jobs = ApifyBatchJob.objects.values_list('id', flat=True)
    print(f"Available job IDs: {list(all_jobs)}")
    
except Exception as e:
    print(f"Error testing ViewSet: {e}")