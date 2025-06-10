#!/usr/bin/env python3
"""
Test webhook specifically for folder ID 46 (sadfewfwfwe2f2f)
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

from brightdata_integration.models import ScraperRequest
from instagram_data.models import InstagramPost, Folder

def create_test_request_for_folder_46():
    """Create a test scraper request for folder ID 46"""
    try:
        folder = Folder.objects.get(id=46)
        print(f"✅ Found folder: {folder.name} (ID: {folder.id})")

        # Create a test scraper request
        request_id = f"test_folder_46_{int(time.time())}"
        scraper_request = ScraperRequest.objects.create(
            platform='instagram',
            target_url='https://www.instagram.com/xpengmalaysia',
            request_id=request_id,
            folder_id=folder.id,
            status='processing'
        )

        print(f"✅ Created test scraper request: {request_id}")
        return request_id, folder

    except Folder.DoesNotExist:
        print("❌ Folder ID 46 not found!")
        return None, None

def test_webhook_with_folder_46(request_id):
    """Test sending webhook data for folder 46"""

    webhook_url = 'http://localhost:8000/api/brightdata/webhook/'

    # Sample Instagram data that would come from BrightData
    sample_data = [
        {
            "url": "https://www.instagram.com/p/test_folder_46/",
            "post_id": f"folder_46_test_{int(time.time())}",
            "user_posted": "xpengmalaysia",
            "description": "🧪 TEST: This is a test post for folder 46 webhook debugging",
            "date_posted": "2024-06-02T12:00:00Z",
            "num_comments": 5,
            "likes": 25,
            "shortcode": "test_folder_46",
            "content_type": "post",
            "hashtags": ["test", "folder46", "webhook"]
        }
    ]

    headers = {
        'Content-Type': 'application/json',
        'X-Platform': 'instagram',
        'X-Snapshot-Id': request_id,
        'User-Agent': 'BrightData-Webhook/1.0'
    }

    print(f"\n📡 Testing webhook for folder 46...")
    print(f"   URL: {webhook_url}")
    print(f"   Request ID: {request_id}")
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

def check_folder_46_after_test():
    """Check if data was saved to folder 46"""
    try:
        folder = Folder.objects.get(id=46)
        posts = InstagramPost.objects.filter(folder=folder)

        print(f"\n🔍 Checking folder 46 after webhook test:")
        print(f"   Folder: {folder.name} (ID: {folder.id})")
        print(f"   Posts count: {posts.count()}")

        if posts.exists():
            print("   Recent posts:")
            for post in posts.order_by('-id')[:5]:
                print(f"      - Post ID: {post.post_id}")
                print(f"        Content: {(post.description or '')[:50]}...")

        return posts.count()

    except Folder.DoesNotExist:
        print("❌ Folder 46 not found!")
        return 0

def main():
    print("🧪 Testing Webhook for Folder 46")
    print("=" * 50)

    # Step 1: Create test scraper request
    request_id, folder = create_test_request_for_folder_46()
    if not request_id:
        return

    # Step 2: Test webhook
    success = test_webhook_with_folder_46(request_id)

    # Step 3: Check results
    if success:
        time.sleep(1)  # Give it a moment to process
        posts_count = check_folder_46_after_test()

        if posts_count > 0:
            print(f"\n🎉 SUCCESS! Webhook working - {posts_count} posts saved to folder 46")
        else:
            print(f"\n⚠️  Webhook call succeeded but no posts saved. Check logs.")
    else:
        print(f"\n❌ Webhook call failed")

    # Step 4: Show how to run a real test
    print(f"\n💡 To test with your actual Instagram target:")
    print(f"   1. Check what URL you're scraping for folder 46")
    print(f"   2. Make sure the scraper request is created properly")
    print(f"   3. Verify the webhook URL is configured in BrightData")

if __name__ == "__main__":
    main()
