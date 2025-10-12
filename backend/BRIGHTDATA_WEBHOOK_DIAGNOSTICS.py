#!/usr/bin/env python3
"""
BrightData Webhook Diagnostics - Check webhook events and snapshot ID matching
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.models import BrightDataWebhookEvent, BrightDataScraperRequest, BrightDataScrapedPost

def check_brightdata_webhooks():
    print("🔍 BRIGHTDATA WEBHOOK DIAGNOSTICS")
    print("=" * 50)
    
    # Check webhook events
    events = BrightDataWebhookEvent.objects.all().order_by('-created_at')
    print(f"\n📡 WEBHOOK EVENTS: {events.count()} total")
    
    if events.exists():
        for event in events[:5]:
            print(f"   Event {event.event_id}")
            print(f"   ├── Snapshot: {event.snapshot_id}")
            print(f"   ├── Status: {event.status}")
            print(f"   ├── Platform: {event.platform}")
            print(f"   └── Created: {event.created_at}")
            print()
    else:
        print("   ❌ NO WEBHOOK EVENTS FOUND!")
        print("   This means BrightData webhooks are not being received!")
        
    # Check scraper requests with snapshot IDs
    requests = BrightDataScraperRequest.objects.all().order_by('-created_at')
    print(f"\n🚀 SCRAPER REQUESTS: {requests.count()} total")
    
    for req in requests[:5]:
        print(f"   Request {req.id}")
        print(f"   ├── Snapshot: {req.snapshot_id or 'NONE'}")
        print(f"   ├── Status: {req.status}")
        print(f"   ├── Folder: {req.folder_id}")
        print(f"   ├── Platform: {req.platform}")
        print(f"   └── Created: {req.created_at}")
        print()
        
    # Check scraped posts
    posts = BrightDataScrapedPost.objects.all()
    print(f"\n📊 SCRAPED POSTS: {posts.count()} total")
    
    # Group posts by folder
    folder_posts = {}
    for post in posts:
        if post.folder_id not in folder_posts:
            folder_posts[post.folder_id] = 0
        folder_posts[post.folder_id] += 1
        
    for folder_id, count in folder_posts.items():
        print(f"   Folder {folder_id}: {count} posts")
        
    # Check for matching snapshot IDs
    print(f"\n🔗 SNAPSHOT ID MATCHING:")
    requests_with_snapshots = BrightDataScraperRequest.objects.exclude(snapshot_id__isnull=True).exclude(snapshot_id='')
    
    if requests_with_snapshots.exists():
        print(f"   Requests with snapshot IDs: {requests_with_snapshots.count()}")
        for req in requests_with_snapshots:
            # Check if there's a matching webhook event
            matching_events = BrightDataWebhookEvent.objects.filter(snapshot_id=req.snapshot_id)
            print(f"   Snapshot {req.snapshot_id}: {matching_events.count()} webhook events")
    else:
        print("   ❌ NO REQUESTS WITH SNAPSHOT IDS!")
        
    print(f"\n🎯 DIAGNOSIS:")
    if events.count() == 0:
        print("   🚨 WEBHOOK PROBLEM: No webhook events received from BrightData")
        print("   🔧 Check webhook URL configuration in BrightData dashboard")
        print("   🔧 Webhook should point to: https://your-domain.com/api/brightdata/webhook/")
    else:
        print(f"   ✅ Webhooks working: {events.count()} events received")
        
    if requests_with_snapshots.count() == 0:
        print("   🚨 SNAPSHOT PROBLEM: No scraper requests have snapshot IDs")
        print("   🔧 Check BrightData API response includes snapshot_id")
    else:
        print(f"   ✅ Snapshot IDs working: {requests_with_snapshots.count()} requests have snapshot IDs")

if __name__ == "__main__":
    check_brightdata_webhooks()