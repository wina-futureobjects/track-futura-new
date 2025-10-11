import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.models import BrightDataScrapedPost, BrightDataWebhookEvent

print("=== DATABASE CHECK ===")

try:
    scraped_count = BrightDataScrapedPost.objects.count()
    print(f"Scraped posts count: {scraped_count}")
    
    if scraped_count > 0:
        latest_posts = BrightDataScrapedPost.objects.order_by('-created_at')[:5]
        print("Latest scraped posts:")
        for post in latest_posts:
            print(f"  - {post.post_id} (folder_{post.folder_id}) {post.created_at}")
except Exception as e:
    print(f"Scraped posts error: {e}")

try:
    webhook_count = BrightDataWebhookEvent.objects.count()
    print(f"Webhook events count: {webhook_count}")
    
    if webhook_count > 0:
        latest_events = BrightDataWebhookEvent.objects.order_by('-created_at')[:5]
        print("Latest webhook events:")
        for event in latest_events:
            print(f"  - {event.platform} {event.status} {event.created_at}")
except Exception as e:
    print(f"Webhook events error: {e}")

print("=== CHECK COMPLETE ===")