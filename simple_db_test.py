import django
import os

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.models import BrightDataWebhookEvent, BrightDataScrapedPost

print("=== DATABASE TEST ===")

# Test webhook events
try:
    webhook_count = BrightDataWebhookEvent.objects.count()
    print(f"Webhook events count: {webhook_count}")
    
    # Get latest webhook events
    latest_events = BrightDataWebhookEvent.objects.order_by('-created_at')[:3]
    for event in latest_events:
        print(f"  - Event {event.id}: {event.platform} {event.status} {event.created_at}")
        
except Exception as e:
    print(f"Webhook events error: {e}")

# Test scraped posts
try:
    posts_count = BrightDataScrapedPost.objects.count()
    print(f"Scraped posts count: {posts_count}")
    
    # Get latest scraped posts
    latest_posts = BrightDataScrapedPost.objects.order_by('-created_at')[:3]
    for post in latest_posts:
        print(f"  - Post {post.id}: {post.post_id} folder_{post.folder_id} {post.created_at}")
        
except Exception as e:
    print(f"Scraped posts error: {e}")

# Test creating a webhook event
try:
    test_event = BrightDataWebhookEvent.objects.create(
        platform="test",
        event_type="webhook", 
        status="received",
        raw_data={"test": "diagnostic"}
    )
    print(f"Created test webhook event ID: {test_event.id}")
    
    # Delete it
    test_event.delete()
    print("Deleted test event")
    
except Exception as e:
    print(f"Create webhook event error: {e}")

print("=== TEST COMPLETE ===")