#!/usr/bin/env python3
"""
Simple Webhook Monitor - Find the exact issue
"""

import os
import sys
import django
import requests
import json

# Setup Django
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.chdir(backend_path)
django.setup()

from brightdata_integration.models import ScraperRequest, BrightdataConfig
from instagram_data.models import InstagramPost, Folder

def check_problem_folder():
    """Check the problem folder specifically"""
    print("🔍 ANALYZING PROBLEM FOLDER")
    print("=" * 50)

    try:
        folder = Folder.objects.get(id=46)
        print(f"✅ Folder found: {folder.name} (ID: {folder.id})")
        print(f"   Created: {folder.created_at}")
        print(f"   Posts: {InstagramPost.objects.filter(folder=folder).count()}")

        # Check for ScraperRequests for this folder
        requests_for_folder = ScraperRequest.objects.filter(folder_id=46).order_by('-created_at')
        print(f"\n📋 ScraperRequests for folder 46:")
        if requests_for_folder.exists():
            for req in requests_for_folder:
                print(f"   - Request ID: {req.request_id}")
                print(f"     Status: {req.status}")
                print(f"     Platform: {req.platform}")
                print(f"     URL: {req.target_url}")
                print(f"     Created: {req.created_at}")
        else:
            print("   ❌ NO SCRAPER REQUESTS FOUND FOR FOLDER 46")
            print("   🔥 THIS IS THE PROBLEM!")

    except Folder.DoesNotExist:
        print("❌ Folder 46 not found")

def check_brightdata_configs():
    """Check BrightData configurations"""
    print(f"\n⚙️  BRIGHTDATA CONFIGURATIONS")
    print("=" * 50)

    configs = BrightdataConfig.objects.all()
    if configs.exists():
        for config in configs:
            print(f"   - {config.name}: {config.platform}")
            print(f"     Dataset ID: {config.dataset_id}")
            print(f"     Active: {config.is_active}")
            print(f"     Token: ***{config.api_token[-4:] if config.api_token else 'None'}")
    else:
        print("   ❌ No BrightData configurations found")

def test_manual_scraper_request():
    """Test creating a manual scraper request for folder 46"""
    print(f"\n🧪 TESTING MANUAL SCRAPER REQUEST")
    print("=" * 50)

    try:
        # Check if we have any BrightData config
        config = BrightdataConfig.objects.filter(platform__icontains='instagram').first()
        if not config:
            config = BrightdataConfig.objects.first()

        if not config:
            print("❌ No BrightData configuration found")
            print("   You need to create a BrightData config first")
            return

        folder = Folder.objects.get(id=46)

        # Create a test scraper request
        import time
        test_request = ScraperRequest.objects.create(
            config=config,
            platform='instagram',
            target_url='https://www.instagram.com/xpengmalaysia',  # Example URL
            request_id=f'manual_test_{int(time.time())}',
            folder_id=folder.id,
            status='processing',
            num_of_posts=5
        )

        print(f"✅ Created test ScraperRequest:")
        print(f"   Request ID: {test_request.request_id}")
        print(f"   Folder ID: {test_request.folder_id}")
        print(f"   Platform: {test_request.platform}")

        return test_request.request_id

    except Exception as e:
        print(f"❌ Error creating test request: {str(e)}")
        return None

def test_webhook_with_request(request_id):
    """Test webhook with the created request"""
    print(f"\n📡 TESTING WEBHOOK WITH REQUEST ID")
    print("=" * 50)

    if not request_id:
        print("❌ No request ID provided")
        return

    webhook_url = 'http://localhost:8000/api/brightdata/webhook/'

    # Sample data that would come from BrightData
    sample_data = [
        {
            "url": "https://www.instagram.com/p/test_manual/",
            "post_id": f"manual_test_{int(__import__('time').time())}",
            "user_posted": "xpengmalaysia",
            "description": "🔧 MANUAL TEST: This is a manual test to verify webhook processing",
            "date_posted": "2024-06-02T15:00:00Z",
            "num_comments": 3,
            "likes": 15,
            "shortcode": "test_manual",
            "content_type": "post"
        }
    ]

    headers = {
        'Content-Type': 'application/json',
        'X-Platform': 'instagram',
        'X-Snapshot-Id': request_id,
        'User-Agent': 'BrightData-Webhook/1.0'
    }

    print(f"   Webhook URL: {webhook_url}")
    print(f"   Request ID: {request_id}")
    print(f"   Sample data: {json.dumps(sample_data[0], indent=2)}")

    try:
        response = requests.post(webhook_url, json=sample_data, headers=headers, timeout=30)
        print(f"\n✅ Webhook Response:")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")

        if response.status_code == 200:
            # Check if data was saved
            __import__('time').sleep(1)
            folder = Folder.objects.get(id=46)
            new_posts = InstagramPost.objects.filter(folder=folder).count()
            print(f"\n📊 After webhook:")
            print(f"   Posts in folder 46: {new_posts}")

            if new_posts > 0:
                print("🎉 SUCCESS! Webhook processing is working!")
                recent_post = InstagramPost.objects.filter(folder=folder).order_by('-id').first()
                print(f"   Latest post: {recent_post.post_id}")
                print(f"   Content: {(recent_post.description or '')[:50]}...")
            else:
                print("⚠️  Webhook succeeded but no posts saved - check processing logic")
        else:
            print("❌ Webhook failed")

    except Exception as e:
        print(f"❌ Webhook error: {str(e)}")

def main():
    print("🚨 SIMPLE WEBHOOK ISSUE DIAGNOSIS")
    print("=" * 60)

    # Step 1: Check the problem folder
    check_problem_folder()

    # Step 2: Check configurations
    check_brightdata_configs()

    # Step 3: Test manual creation
    request_id = test_manual_scraper_request()

    # Step 4: Test webhook
    if request_id:
        test_webhook_with_request(request_id)

    print(f"\n💡 DIAGNOSIS COMPLETE")
    print("=" * 60)
    print("If the manual test worked, the issue is:")
    print("1. You're not creating ScraperRequests when starting scrapes")
    print("2. Use your app's scraper interface instead of BrightData dashboard")
    print("3. Make sure the app creates ScraperRequest with folder_id before scraping")

if __name__ == "__main__":
    main()
