#!/usr/bin/env python
"""
Check webhook delivery status
"""
import os
import sys
import django

# Setup Django environment
sys.path.append('backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trackfutura.settings')
django.setup()

from brightdata_integration.models import BrightDataWebhookEvent, BrightDataScrapedPost, BrightDataScraperRequest

print("=" * 60)
print("🔍 WEBHOOK DELIVERY STATUS CHECK")
print("=" * 60)

# Check recent webhook events
print("\n📡 RECENT WEBHOOK EVENTS:")
recent_events = BrightDataWebhookEvent.objects.order_by('-created_at')[:10]
if recent_events:
    for event in recent_events:
        data_count = len(event.raw_data) if event.raw_data else 0
        print(f"  {event.created_at.strftime('%Y-%m-%d %H:%M:%S')} | {event.event_id} | {event.status} | {event.platform} | {data_count} items")
else:
    print("  ❌ No webhook events found")

# Check scraped posts from webhooks
print("\n📊 RECENT SCRAPED POSTS:")
recent_posts = BrightDataScrapedPost.objects.order_by('-created_at')[:10]
if recent_posts:
    for post in recent_posts:
        webhook_flag = "🎯 WEBHOOK" if post.webhook_delivered else "📡 POLLING"
        print(f"  {post.created_at.strftime('%Y-%m-%d %H:%M:%S')} | {webhook_flag} | {post.platform} | Folder {post.folder_id} | {post.user_posted} | {post.post_id}")
else:
    print("  ❌ No scraped posts found")

# Check recent scraper requests
print("\n🔄 RECENT SCRAPER REQUESTS:")
recent_requests = BrightDataScraperRequest.objects.order_by('-created_at')[:10]
if recent_requests:
    for req in recent_requests:
        print(f"  {req.created_at.strftime('%Y-%m-%d %H:%M:%S')} | ID {req.id} | {req.platform} | {req.status} | Folder {req.folder_id} | {req.snapshot_id or 'No Snapshot'}")
else:
    print("  ❌ No scraper requests found")

# Statistics
print("\n📈 DELIVERY STATISTICS:")
total_webhook_events = BrightDataWebhookEvent.objects.count()
total_scraped_posts = BrightDataScrapedPost.objects.count()
webhook_delivered_posts = BrightDataScrapedPost.objects.filter(webhook_delivered=True).count()
polling_delivered_posts = BrightDataScrapedPost.objects.filter(webhook_delivered=False).count()

print(f"  Total Webhook Events: {total_webhook_events}")
print(f"  Total Scraped Posts: {total_scraped_posts}")
print(f"  Webhook Delivered: {webhook_delivered_posts}")
print(f"  Polling Delivered: {polling_delivered_posts}")

# Check if webhook endpoint is being called
print(f"\n🎯 WEBHOOK DELIVERY RATE: {webhook_delivered_posts}/{total_scraped_posts} posts delivered via webhook")

if webhook_delivered_posts == 0 and total_webhook_events > 0:
    print("⚠️ WARNING: Webhooks are being received but not creating scraped posts!")
    print("🔍 Check the _process_brightdata_results function")
elif total_webhook_events == 0:
    print("⚠️ WARNING: No webhook events received at all!")
    print("🔍 Check BrightData webhook configuration")
else:
    print("✅ Webhook delivery appears to be working")

print("\n" + "=" * 60)