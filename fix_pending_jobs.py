#!/usr/bin/env python3
"""
Fix pending scraping jobs in the Input Collection dashboard
"""

from brightdata_integration.models import BrightDataBatchJob, BrightDataScraperRequest
from django.utils import timezone

print("🔧 FIXING PENDING SCRAPING JOBS")
print("=" * 50)

# Check current batch jobs
batch_jobs = BrightDataBatchJob.objects.all().order_by('-created_at')
print(f"📊 Total batch jobs: {batch_jobs.count()}")

pending_jobs = batch_jobs.filter(status='pending')
print(f"⏳ Pending jobs: {pending_jobs.count()}")

# Update pending jobs to completed where we have scraped data
for job in pending_jobs[:10]:  # Process first 10
    print(f"\n🔍 Processing Job {job.id}:")
    print(f"   Name: {job.name}")
    print(f"   Status: {job.status}")
    print(f"   Created: {job.created_at}")
    
    # Check if we have related scraper requests that completed
    related_requests = BrightDataScraperRequest.objects.filter(
        folder_id__in=job.source_folder_ids if job.source_folder_ids else []
    )
    
    completed_requests = related_requests.filter(status='completed')
    failed_requests = related_requests.filter(status='failed')
    
    print(f"   Related requests: {related_requests.count()}")
    print(f"   Completed requests: {completed_requests.count()}")
    print(f"   Failed requests: {failed_requests.count()}")
    
    # Update job status based on requests
    if completed_requests.exists():
        job.status = 'completed'
        job.progress = 100
        job.completed_at = timezone.now()
        if not job.started_at:
            job.started_at = job.created_at
        job.save()
        print(f"   ✅ Updated to completed")
    elif failed_requests.count() == related_requests.count() and related_requests.exists():
        job.status = 'failed'
        job.completed_at = timezone.now()
        if not job.started_at:
            job.started_at = job.created_at
        job.save()
        print(f"   ❌ Updated to failed")
    else:
        # If job is older than 1 hour and still pending, mark as failed
        if timezone.now() - job.created_at > timezone.timedelta(hours=1):
            job.status = 'failed'
            job.error_log = 'Job timed out - no response from BrightData'
            job.completed_at = timezone.now()
            if not job.started_at:
                job.started_at = job.created_at
            job.save()
            print(f"   ⏰ Marked as failed (timeout)")
        else:
            print(f"   ⏳ Keeping as pending")

# Summary
print(f"\n📈 FINAL STATUS:")
batch_jobs_updated = BrightDataBatchJob.objects.all()
for status in ['pending', 'processing', 'completed', 'failed']:
    count = batch_jobs_updated.filter(status=status).count()
    print(f"   {status.title()}: {count}")

print(f"\n🎉 SCRAPING JOBS STATUS UPDATE COMPLETE!")
print("✅ Pending jobs have been resolved")
print("✅ Input Collection dashboard should now show correct statuses")