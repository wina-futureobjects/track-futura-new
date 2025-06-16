#!/usr/bin/env python3
"""
Test script to debug the webhook issue with BrightData Instagram data
"""

import json
import requests
import os
import sys
import time

# Add Django project to path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from instagram_data.models import Folder, InstagramPost
from brightdata_integration.models import ScraperRequest, BrightdataNotification, BrightdataConfig

def test_webhook_with_real_data():
    """Test webhook processing with the actual JSON data from user"""

    print("🔍 TESTING WEBHOOK WITH REAL BRIGHTDATA JSON")
    print("=" * 60)

    # Load the actual JSON data from user's file
    try:
        with open('bd_20250616_040447_0.json', 'r') as f:
            webhook_data = json.load(f)
        print(f"✅ Loaded JSON data with {len(webhook_data)} entries")
    except FileNotFoundError:
        print("❌ JSON file not found. Using sample data instead.")
        # Fallback to sample data based on the user's attachment
        webhook_data = [
            {"timestamp":"2025-06-16T04:04:52.426Z","input":{"url":"https://www.instagram.com/mycarforum","num_of_posts":2,"posts_to_not_include":[],"start_date":"06-01-2025","end_date":"06-16-2025","post_type":"Post"},"warning":"no posts found, please check pinned posts detection","warning_code":"dead_page"},
            {"url":"https://www.instagram.com/p/DKeLi2VSshg","user_posted":"sgcarmart","description":"COE premiums fell across all categories this round! 📉\n\n👉 Full breakdown at sgcarmart.com/coe-price","num_comments":1,"date_posted":"2025-06-04T08:06:44.000Z","likes":167,"photos":["https://scontent-hou1-1.cdninstagram.com/v/t51.2885-15/504147703_18502322356012500_4857974309411431305_n.jpg"],"post_id":"3647403521529792608","shortcode":"DKeLi2VSshg","content_type":"Image","pk":"3647403521529792608","content_id":"DKeLi2VSshg","thumbnail":"https://scontent-hou1-1.cdninstagram.com/v/t51.2885-15/504147703_18502322356012500_4857974309411431305_n.jpg","followers":30522,"posts_count":3858,"profile_image_link":"https://scontent-hou1-1.cdninstagram.com/v/t51.2885-19/290390140_759663418539113_5957964713519705967_n.jpg","is_verified":True,"is_paid_partnership":False,"user_posted_id":"286028499"}
        ]

    # Create test folder
    test_folder, created = Folder.objects.get_or_create(
        name="Webhook Test Folder - June 16",
        defaults={"description": "Testing webhook with real BrightData JSON"}
    )
    print(f"📁 Test folder: {test_folder.name} (ID: {test_folder.id})")

    # Create config and scraper request
    config, created = BrightdataConfig.objects.get_or_create(
        platform='instagram_posts',
        defaults={'name': 'Instagram Posts Config', 'dataset_id': 'gd_l7q7dkz2twe8xh', 'is_active': True}
    )

    scraper_request = ScraperRequest.objects.create(
        config=config,
        platform='instagram_posts',
        content_type='post',
        target_url='https://www.instagram.com/sgcarmart/',
        folder_id=test_folder.id,
        status='processing',
        request_id='test_webhook_16_june'
    )
    print(f"📋 Created scraper request: ID {scraper_request.id}")

    # Count posts before
    initial_count = InstagramPost.objects.filter(folder=test_folder).count()
    print(f"📊 Initial Instagram posts in folder: {initial_count}")

    # Analyze the data structure
    print(f"\n🔍 ANALYZING JSON DATA STRUCTURE")
    valid_posts = 0
    warning_entries = 0

    for i, entry in enumerate(webhook_data):
        if entry.get('warning') or entry.get('error') or entry.get('warning_code'):
            warning_entries += 1
            print(f"  ⚠️  Entry {i+1}: Warning - {entry.get('warning', entry.get('error', 'Unknown'))}")
        elif entry.get('url') or entry.get('post_id') or entry.get('pk'):
            valid_posts += 1
            post_id = entry.get('post_id') or entry.get('pk')
            url = entry.get('url', 'No URL')
            user = entry.get('user_posted', 'No user')
            print(f"  ✅ Entry {i+1}: Valid post - {post_id} by {user}")
        else:
            print(f"  ❓ Entry {i+1}: Missing required fields")

    print(f"\n📈 Data Summary:")
    print(f"  • Total entries: {len(webhook_data)}")
    print(f"  • Valid posts: {valid_posts}")
    print(f"  • Warning entries: {warning_entries}")

    # Test the webhook endpoint
    print(f"\n🌐 TESTING WEBHOOK ENDPOINT")
    webhook_url = "http://localhost:8000/api/brightdata/webhook/"
    headers = {
        "Content-Type": "application/json",
        "X-Snapshot-Id": scraper_request.request_id,
        "X-Platform": "instagram"
    }

    try:
        response = requests.post(
            webhook_url,
            json=webhook_data,
            headers=headers,
            timeout=30
        )
        print(f"📡 Webhook response status: {response.status_code}")
        print(f"📄 Response content: {response.text[:500]}...")

        if response.status_code == 200:
            print("✅ Webhook request successful")
        else:
            print(f"❌ Webhook request failed: {response.status_code}")

    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to webhook endpoint. Is the Django server running?")
        return
    except Exception as e:
        print(f"❌ Webhook test failed: {str(e)}")
        return

    # Wait a moment for processing
    time.sleep(2)

    # Check if posts were created
    final_count = InstagramPost.objects.filter(folder=test_folder).count()
    posts_created = final_count - initial_count

    print(f"\n📊 RESULTS:")
    print(f"  • Posts in folder before: {initial_count}")
    print(f"  • Posts in folder after: {final_count}")
    print(f"  • Posts created: {posts_created}")

    if posts_created > 0:
        print("✅ SUCCESS: Posts were created!")
        # Show details of created posts
        created_posts = InstagramPost.objects.filter(folder=test_folder).order_by('-id')[:posts_created]
        for post in created_posts:
            print(f"  📝 Created post: {post.post_id} by {post.user_posted}")
    else:
        print("❌ ISSUE: No posts were created!")

                # Debug: Check if any Instagram posts were created at all
        from django.utils import timezone
        from datetime import timedelta
        recent_posts = InstagramPost.objects.filter(
            created_at__gte=timezone.now() - timedelta(minutes=5)
        ).count()
        print(f"  🔍 Recent Instagram posts (last 5 min): {recent_posts}")

        # Check scraper request status
        scraper_request.refresh_from_db()
        print(f"  📋 Scraper request status: {scraper_request.status}")

        # Check for any notifications
        recent_notifications = BrightdataNotification.objects.filter(
            created_at__gte=timezone.now() - timedelta(minutes=5)
        )
        print(f"  📢 Recent notifications: {recent_notifications.count()}")
        for notification in recent_notifications[:3]:
            print(f"    • {notification.notification_type}: {notification.message[:100]}")

def test_field_mapping():
    """Test the field mapping function with sample data"""

    print(f"\n🗂️  TESTING FIELD MAPPING")

    # Sample post data from the JSON
    sample_post = {
        "url": "https://www.instagram.com/p/DKeLi2VSshg",
        "user_posted": "sgcarmart",
        "description": "COE premiums fell across all categories this round! 📉\n\n👉 Full breakdown at sgcarmart.com/coe-price",
        "num_comments": 1,
        "date_posted": "2025-06-04T08:06:44.000Z",
        "likes": 167,
        "photos": ["https://scontent-hou1-1.cdninstagram.com/photo.jpg"],
        "post_id": "3647403521529792608",
        "shortcode": "DKeLi2VSshg",
        "content_type": "Image",
        "pk": "3647403521529792608",
        "content_id": "DKeLi2VSshg",
        "followers": 30522,
        "posts_count": 3858,
        "is_verified": True,
        "user_posted_id": "286028499"
    }

    # Test field mapping
    from brightdata_integration.views import _map_post_fields
    mapped_fields = _map_post_fields(sample_post, 'instagram')

    print(f"Mapped fields:")
    for key, value in mapped_fields.items():
        if value:  # Only show non-empty values
            print(f"  • {key}: {str(value)[:100]}{'...' if len(str(value)) > 100 else ''}")

if __name__ == "__main__":
    test_field_mapping()
    test_webhook_with_real_data()
