"""
Diagnostic script to check Apify data storage issues
"""
import os
import sys
import django

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Setup Django
django.setup()

from apify_integration.models import ApifyScraperRequest, ApifyBatchJob, ApifyWebhookEvent
from django.utils import timezone
from datetime import timedelta

def check_apify_data_storage():
    print("=== Apify Data Storage Diagnostic ===\n")
    
    # Check recent scraper requests
    print("1. Recent Scraper Requests (last 7 days):")
    recent_requests = ApifyScraperRequest.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=7)
    ).order_by('-created_at')
    
    if recent_requests.exists():
        for req in recent_requests[:10]:
            print(f"  ID: {req.id}")
            print(f"  Platform: {req.platform}")
            print(f"  Status: {req.status}")
            print(f"  Request ID: {req.request_id}")
            print(f"  Target URL: {req.target_url}")
            print(f"  Error: {req.error_message or 'None'}")
            print(f"  Created: {req.created_at}")
            print("  ---")
    else:
        print("  No recent scraper requests found")
    
    print("\n2. Recent Batch Jobs (last 7 days):")
    recent_jobs = ApifyBatchJob.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=7)
    ).order_by('-created_at')
    
    if recent_jobs.exists():
        for job in recent_jobs[:5]:
            print(f"  ID: {job.id}")
            print(f"  Name: {job.name}")
            print(f"  Status: {job.status}")
            print(f"  Project: {job.project_id if job.project else 'None'}")
            print(f"  Source Folders: {job.source_folder_ids}")
            print(f"  Created: {job.created_at}")
            print("  ---")
    else:
        print("  No recent batch jobs found")
    
    print("\n3. Recent Webhook Events (last 24 hours):")
    recent_webhooks = ApifyWebhookEvent.objects.filter(
        created_at__gte=timezone.now() - timedelta(hours=24)
    ).order_by('-created_at')
    
    if recent_webhooks.exists():
        for webhook in recent_webhooks[:5]:
            print(f"  Event ID: {webhook.event_id}")
            print(f"  Run ID: {webhook.run_id}")
            print(f"  Status: {webhook.status}")
            print(f"  Platform: {webhook.platform}")
            print(f"  Created: {webhook.created_at}")
            print("  ---")
    else:
        print("  No recent webhook events found")
    
    print("\n4. Data Storage Status Check:")
    
    # Check if there are any completed requests without processed data
    completed_requests = ApifyScraperRequest.objects.filter(status='completed')
    print(f"  Total completed requests: {completed_requests.count()}")
    
    # Check Instagram data
    try:
        from instagram_data.models import InstagramPost, Folder as InstagramFolder
        instagram_posts = InstagramPost.objects.all().count()
        instagram_folders = InstagramFolder.objects.all().count()
        print(f"  Instagram posts stored: {instagram_posts}")
        print(f"  Instagram folders: {instagram_folders}")
    except Exception as e:
        print(f"  Error checking Instagram data: {e}")
    
    # Check Facebook data
    try:
        from facebook_data.models import FacebookPost, Folder as FacebookFolder
        facebook_posts = FacebookPost.objects.all().count()
        facebook_folders = FacebookFolder.objects.all().count()
        print(f"  Facebook posts stored: {facebook_posts}")
        print(f"  Facebook folders: {facebook_folders}")
    except Exception as e:
        print(f"  Error checking Facebook data: {e}")
    
    # Check TikTok data
    try:
        from tiktok_data.models import TikTokPost, Folder as TikTokFolder
        tiktok_posts = TikTokPost.objects.all().count()
        tiktok_folders = TikTokFolder.objects.all().count()
        print(f"  TikTok posts stored: {tiktok_posts}")
        print(f"  TikTok folders: {tiktok_folders}")
    except Exception as e:
        print(f"  Error checking TikTok data: {e}")
    
    print("\n5. Configuration Check:")
    
    # Check Apify configs
    from apify_integration.models import ApifyConfig
    configs = ApifyConfig.objects.all()
    print(f"  Apify configurations: {configs.count()}")
    
    for config in configs:
        print(f"    Platform: {config.platform}")
        print(f"    Actor ID: {config.actor_id}")
        print(f"    Has API Token: {'Yes' if config.api_token else 'No'}")
        print("    ---")

if __name__ == "__main__":
    check_apify_data_storage()