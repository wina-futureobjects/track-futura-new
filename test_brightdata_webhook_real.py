#!/usr/bin/env python3
"""
Test script to debug the webhook issue with exact BrightData Instagram data
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
from django.utils import timezone
from datetime import timedelta

def test_webhook_with_exact_data():
    """Test webhook processing with the exact JSON data from user's file"""

    print("🔍 TESTING WEBHOOK WITH EXACT BRIGHTDATA JSON")
    print("=" * 60)

    # Use the exact JSON data from the user's attached file
    webhook_data = [
        {
            "timestamp": "2025-06-16T04:04:52.426Z",
            "input": {
                "url": "https://www.instagram.com/mycarforum",
                "num_of_posts": 2,
                "posts_to_not_include": [],
                "start_date": "06-01-2025",
                "end_date": "06-16-2025",
                "post_type": "Post"
            },
            "warning": "no posts found, please check pinned posts detection",
            "warning_code": "dead_page"
        },
        {
            "timestamp": "2025-06-16T04:04:55.033Z",
            "input": {
                "url": "https://www.instagram.com/torque.sg",
                "num_of_posts": 2,
                "posts_to_not_include": [],
                "start_date": "06-01-2025",
                "end_date": "06-16-2025",
                "post_type": "Post"
            },
            "warning": "no posts found, please check pinned posts detection",
            "warning_code": "dead_page"
        },
        {
            "url": "https://www.instagram.com/p/DKeLi2VSshg",
            "user_posted": "sgcarmart",
            "description": "COE premiums fell across all categories this round! 📉\n\n👉 Full breakdown at sgcarmart.com/coe-price",
            "num_comments": 1,
            "date_posted": "2025-06-04T08:06:44.000Z",
            "likes": 167,
            "photos": ["https://scontent-hou1-1.cdninstagram.com/v/t51.2885-15/504147703_18502322356012500_4857974309411431305_n.jpg"],
            "latest_comments": [{"comments": "Cheap!", "user_commenting": "_l_do.0b_l_", "likes": 0}],
            "post_id": "3647403521529792608",
            "shortcode": "DKeLi2VSshg",
            "content_type": "Image",
            "pk": "3647403521529792608",
            "content_id": "DKeLi2VSshg",
            "thumbnail": "https://scontent-hou1-1.cdninstagram.com/v/t51.2885-15/504147703_thumb.jpg",
            "followers": 30522,
            "posts_count": 3858,
            "profile_image_link": "https://scontent-hou1-1.cdninstagram.com/v/t51.2885-19/290390140_759663418539113_5957964713519705967_n.jpg",
            "is_verified": True,
            "is_paid_partnership": False,
            "partnership_details": {"profile_id": None, "username": None, "profile_url": None},
            "user_posted_id": "286028499",
            "post_content": [{"index": 0, "type": "Photo", "url": "https://scontent-hou1-1.cdninstagram.com/photo.jpg", "id": "3647403521529792608"}],
            "profile_url": "https://www.instagram.com/sgcarmart",
            "timestamp": "2025-06-16T04:05:01.055Z",
            "input": {"url": "https://www.instagram.com/p/DKeLi2VSshg"},
            "discovery_input": {"url": "https://www.instagram.com/sgcarmart", "num_of_posts": 2}
        },
        {
            "url": "https://www.instagram.com/p/DKvYwL_S9R4",
            "user_posted": "oneshift",
            "description": "Visiting the BYD History Museum: The Electric Dream spanned Generations",
            "num_comments": 0,
            "date_posted": "2025-06-11T00:29:14.000Z",
            "likes": 6,
            "photos": ["https://scontent-atl3-3.cdninstagram.com/v/t51.2885-15/505768475_18506454094058481_22646001212356528_n.jpg"],
            "post_id": "3652246687345005688",
            "shortcode": "DKvYwL_S9R4",
            "content_type": "Carousel",
            "pk": "3652246687345005688",
            "content_id": "DKvYwL_S9R4",
            "thumbnail": "https://scontent-atl3-3.cdninstagram.com/v/t51.2885-15/505768475_thumb.jpg",
            "followers": 2799,
            "posts_count": 1431,
            "profile_image_link": "https://scontent-atl3-3.cdninstagram.com/v/t51.2885-19/100616514_274729840334671_2062863674053230592_n.jpg",
            "is_verified": False,
            "is_paid_partnership": False,
            "user_posted_id": "365306480",
            "profile_url": "https://www.instagram.com/oneshift",
            "timestamp": "2025-06-16T04:05:01.330Z"
        }
    ]

    print(f"✅ Using exact JSON data with {len(webhook_data)} entries")

    # Create test folder
    test_folder, created = Folder.objects.get_or_create(
        name="Real Webhook Test - June 16",
        defaults={"description": "Testing with exact BrightData JSON structure"}
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
        request_id='real_webhook_test_june16'
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
            print(f"      URL: {url}")
        else:
            print(f"  ❓ Entry {i+1}: Missing required fields")

    print(f"\n📈 Data Summary:")
    print(f"  • Total entries: {len(webhook_data)}")
    print(f"  • Valid posts: {valid_posts}")
    print(f"  • Warning entries: {warning_entries}")

    # Test direct function call first
    print(f"\n🔧 TESTING DIRECT FUNCTION CALL")
    from brightdata_integration.views import _process_webhook_data
    try:
        result = _process_webhook_data(webhook_data, 'instagram', scraper_request)
        print(f"📋 Direct function result: {result}")
    except Exception as e:
        print(f"❌ Direct function failed: {str(e)}")
        import traceback
        traceback.print_exc()

    # Check posts after direct call
    intermediate_count = InstagramPost.objects.filter(folder=test_folder).count()
    posts_from_direct = intermediate_count - initial_count
    print(f"📊 Posts created from direct call: {posts_from_direct}")

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
        print("❌ Could not connect to webhook endpoint. Is the Django server running on localhost:8000?")
        print("💡 Try running: cd backend && python manage.py runserver")
    except Exception as e:
        print(f"❌ Webhook test failed: {str(e)}")

    # Wait a moment for processing
    time.sleep(2)

    # Check final results
    final_count = InstagramPost.objects.filter(folder=test_folder).count()
    total_posts_created = final_count - initial_count

    print(f"\n📊 FINAL RESULTS:")
    print(f"  • Posts in folder before: {initial_count}")
    print(f"  • Posts in folder after: {final_count}")
    print(f"  • Total posts created: {total_posts_created}")

    if total_posts_created > 0:
        print("✅ SUCCESS: Posts were created!")
        # Show details of created posts
        created_posts = InstagramPost.objects.filter(folder=test_folder).order_by('-id')[:total_posts_created]
        for post in created_posts:
            print(f"  📝 Created post: {post.post_id} by {post.user_posted}")
            print(f"      Likes: {post.likes}, Comments: {post.num_comments}")
    else:
        print("❌ ISSUE: No posts were created!")

        # Debug recent posts
        recent_posts = InstagramPost.objects.filter(
            created_at__gte=timezone.now() - timedelta(minutes=5)
        ).count()
        print(f"  🔍 Recent Instagram posts (last 5 min): {recent_posts}")

        # Check scraper request status
        scraper_request.refresh_from_db()
        print(f"  📋 Scraper request status: {scraper_request.status}")

        # Check for any recent notifications
        recent_notifications = BrightdataNotification.objects.filter(
            created_at__gte=timezone.now() - timedelta(minutes=5)
        )
        print(f"  📢 Recent notifications: {recent_notifications.count()}")
        for notification in recent_notifications[:3]:
            print(f"    • {notification.notification_type}: {notification.message[:100]}")

def test_individual_post():
    """Test processing of a single valid post"""
    print(f"\n🔬 TESTING INDIVIDUAL POST PROCESSING")

    single_post = {
        "url": "https://www.instagram.com/p/DKeLi2VSshg",
        "user_posted": "sgcarmart",
        "description": "COE premiums fell across all categories this round! 📉\n\n👉 Full breakdown at sgcarmart.com/coe-price",
        "num_comments": 1,
        "date_posted": "2025-06-04T08:06:44.000Z",
        "likes": 167,
        "photos": ["https://scontent-hou1-1.cdninstagram.com/v/t51.2885-15/504147703_photo.jpg"],
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
    mapped_fields = _map_post_fields(single_post, 'instagram')

    print(f"Single post mapped fields:")
    for key, value in mapped_fields.items():
        if value:  # Only show non-empty values
            print(f"  • {key}: {str(value)[:100]}{'...' if len(str(value)) > 100 else ''}")

    # Test direct creation
    try:
        # Create a single post to verify the model works
        test_post = InstagramPost.objects.create(**mapped_fields)
        print(f"✅ Successfully created test post: {test_post.post_id}")
        # Clean up
        test_post.delete()
    except Exception as e:
        print(f"❌ Failed to create test post: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_individual_post()
    test_webhook_with_exact_data()
