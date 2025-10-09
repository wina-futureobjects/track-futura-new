from brightdata_integration.models import BrightDataBatchJob
from django.utils import timezone

print("🔧 UPDATING PROCESSING JOBS")
print("=" * 40)

processing_jobs = BrightDataBatchJob.objects.filter(status='processing')
print(f"Found {processing_jobs.count()} processing jobs")

updated_count = 0
for job in processing_jobs:
    # If job is older than 30 minutes, mark as completed or failed
    if timezone.now() - job.created_at > timezone.timedelta(minutes=30):
        # Check if we have any scraped data for this job's folders
        if job.source_folder_ids:
            from brightdata_integration.models import BrightDataScrapedPost
            posts_exist = BrightDataScrapedPost.objects.filter(
                folder_id__in=job.source_folder_ids
            ).exclude(post_id__startswith='sample_post_').exists()
            
            if posts_exist:
                job.status = 'completed'
                job.progress = 100
                print(f"  ✅ Job {job.id} completed (has data)")
            else:
                job.status = 'failed'
                job.error_log = 'No data received'
                print(f"  ❌ Job {job.id} failed (no data)")
        else:
            job.status = 'failed'
            job.error_log = 'No folder IDs specified'
            print(f"  ❌ Job {job.id} failed (no folders)")
        
        job.completed_at = timezone.now()
        if not job.started_at:
            job.started_at = job.created_at
        job.save()
        updated_count += 1

print(f"\n📊 Updated {updated_count} jobs")

# Final status
print(f"\nFINAL STATUS:")
for status in ['pending', 'processing', 'completed', 'failed']:
    count = BrightDataBatchJob.objects.filter(status=status).count()
    print(f"  {status.title()}: {count}")

print(f"\n🎉 ALL JOBS STATUS UPDATED!")