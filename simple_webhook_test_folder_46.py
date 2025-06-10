#!/usr/bin/env python3
"""
Simple webhook test for folder 46 without creating scraper requests
"""

import requests
import json
import time
import os
import sys
import django

# Setup Django for database access
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.chdir(backend_path)
django.setup()

from instagram_data.models import InstagramPost, Folder

def test_direct_webhook():
    """Test webhook directly without scraper request"""

    webhook_url = 'http://localhost:8000/api/brightdata/webhook/'

    # First, let's just test the webhook endpoint is working
    try:
        response = requests.get('http://localhost:8000/api/brightdata/webhook/health/')
        print(f"🔍 Webhook health check: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return False

    # Sample Instagram data for testing
    sample_data = [
        {
            "url": "https://www.instagram.com/p/test_direct_46/",
            "post_id": f"direct_test_46_{int(time.time())}",
            "user_posted": "test_user",
            "description": "🧪 DIRECT TEST: This is a direct webhook test for debugging",
            "date_posted": "2024-06-02T12:00:00Z",
            "num_comments": 5,
            "likes": 25,
            "shortcode": "test_direct_46",
            "content_type": "post",
            "hashtags": ["test", "direct", "webhook"]
        }
    ]

    headers = {
        'Content-Type': 'application/json',
        'X-Platform': 'instagram',
        'X-Snapshot-Id': 'direct_test_no_request',
        'User-Agent': 'BrightData-Webhook/1.0'
    }

    print(f"\n📡 Testing direct webhook...")
    print(f"   URL: {webhook_url}")
    print(f"   Sample data: {json.dumps(sample_data, indent=2)}")

    try:
        response = requests.post(
            webhook_url,
            json=sample_data,
            headers=headers,
            timeout=30
        )

        print(f"\n✅ Response Status: {response.status_code}")
        print(f"Response Text: {response.text}")

        return response.status_code == 200

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def check_recent_posts():
    """Check recent Instagram posts"""
    print(f"\n🔍 Recent Instagram posts:")
    recent_posts = InstagramPost.objects.order_by('-id')[:5]

    for post in recent_posts:
        folder_info = f"Folder: {post.folder.name} (ID: {post.folder.id})" if post.folder else "No Folder"
        print(f"   - Post ID: {post.post_id}")
        print(f"     {folder_info}")
        print(f"     Content: {(post.description or '')[:50]}...")
        print()

def main():
    print("🧪 Simple Direct Webhook Test")
    print("=" * 40)

    print("\n1️⃣ Checking current state...")
    check_recent_posts()

    print("\n2️⃣ Testing webhook...")
    success = test_direct_webhook()

    if success:
        print("\n3️⃣ Checking if new posts were created...")
        time.sleep(1)
        check_recent_posts()

    print(f"\n💡 Key Points:")
    print(f"   - This test shows if the webhook endpoint works at all")
    print(f"   - If no new posts appear, the issue might be:")
    print(f"     * No scraper request exists for the data")
    print(f"     * BrightData isn't sending webhooks")
    print(f"     * Webhook authentication issues")

if __name__ == "__main__":
    main()
