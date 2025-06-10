#!/usr/bin/env python
"""
Comprehensive debugging script for Track-Futura data flow
Tests the entire pipeline from ScraperRequest creation to webhook processing
"""

import os
import sys
import django
import json
import requests
from datetime import datetime

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.models import BrightdataConfig, ScraperRequest
from instagram_data.models import Folder, InstagramPost

def debug_data_flow():
    """Debug the complete data flow"""
    print("=== TRACK-FUTURA DATA FLOW DEBUG ===\n")

    # 1. Check database state
    print("1. DATABASE STATE:")
    folders = Folder.objects.all()
    posts = InstagramPost.objects.all()
    scraper_requests = ScraperRequest.objects.all()
    configs = BrightdataConfig.objects.filter(platform__icontains='instagram')

    print(f"- Instagram Folders: {folders.count()}")
    print(f"- Instagram Posts: {posts.count()}")
    print(f"- Scraper Requests: {scraper_requests.count()}")
    print(f"- BrightData Configs: {configs.count()}")

    # 2. Check if we have a problematic folder (the one mentioned)
    problem_folder = folders.filter(name__icontains='sadfewfwfwe2f2f').first()
    if problem_folder:
        print(f"\n- Problem folder found: ID={problem_folder.id}, Name='{problem_folder.name}'")
        folder_posts = posts.filter(folder=problem_folder)
        print(f"- Posts in problem folder: {folder_posts.count()}")

        # Check for scraper requests for this folder
        folder_requests = scraper_requests.filter(folder_id=problem_folder.id)
        print(f"- Scraper requests for folder: {folder_requests.count()}")

        if folder_requests.exists():
            for req in folder_requests:
                print(f"  - Request ID: {req.id}, Status: {req.status}, Created: {req.created_at}")

    # 3. Show recent scraper requests
    print(f"\n2. RECENT SCRAPER REQUESTS (last 5):")
    recent_requests = scraper_requests.order_by('-created_at')[:5]
    for req in recent_requests:
        print(f"- ID: {req.id}, Platform: {req.platform}, Status: {req.status}")
        print(f"  URL: {req.target_url}")
        print(f"  Folder ID: {req.folder_id}")
        print(f"  Request ID: {req.request_id}")
        print(f"  Created: {req.created_at}")
        print()

    # 4. Test webhook processing with mock data
    print("3. TESTING WEBHOOK PROCESSING:")

    # Create a test ScraperRequest if none exist
    active_config = configs.filter(platform='instagram_posts', is_active=True).first()
    if not active_config:
        print("- No active Instagram config found!")
        return

    test_request = ScraperRequest.objects.create(
        config=active_config,
        platform='instagram',
        content_type='post',
        target_url='https://www.instagram.com/test/',
        num_of_posts=5,
        folder_id=problem_folder.id if problem_folder else None,
        request_id='debug_test_' + str(int(datetime.now().timestamp())),
        status='pending'
    )
    print(f"- Created test ScraperRequest: ID={test_request.id}")

    # Test webhook data processing
    mock_webhook_data = [
        {
            "url": "https://www.instagram.com/p/test123/",
            "caption": "Test post caption",
            "likes": 100,
            "comments": 50,
            "date": "2025-01-01T12:00:00Z",
            "post_id": "test123",
            "user_name": "testuser",
            "user_id": "123456789"
        }
    ]

    # Test the webhook endpoint
    webhook_url = "http://localhost:8000/api/brightdata/webhook/"
    headers = {
        "Content-Type": "application/json",
        "X-Snapshot-Id": test_request.request_id,
        "X-Platform": "instagram"
    }

    try:
        response = requests.post(webhook_url,
                               json=mock_webhook_data,
                               headers=headers,
                               timeout=10)
        print(f"- Webhook response: {response.status_code}")
        print(f"- Response data: {response.json()}")

        # Check if data was created
        test_posts = InstagramPost.objects.filter(post_id='test123')
        print(f"- Posts created from webhook: {test_posts.count()}")

        # Check scraper request status
        test_request.refresh_from_db()
        print(f"- ScraperRequest status: {test_request.status}")

    except Exception as e:
        print(f"- Webhook test failed: {e}")

    # 5. Check for common issues
    print(f"\n4. CHECKING COMMON ISSUES:")

    # Check for duplicate posts
    from django.db.models import Count
    duplicate_posts = InstagramPost.objects.values('post_id').annotate(
        count=Count('post_id')
    ).filter(count__gt=1)
    print(f"- Duplicate posts by post_id: {duplicate_posts.count()}")

    # Check for posts without folders
    orphaned_posts = posts.filter(folder__isnull=True)
    print(f"- Posts without folders: {orphaned_posts.count()}")

    # Check for scraper requests without folder_id
    requests_no_folder = scraper_requests.filter(folder_id__isnull=True)
    print(f"- ScraperRequests without folder_id: {requests_no_folder.count()}")

    # Show folder-post distribution
    print(f"\n5. FOLDER-POST DISTRIBUTION:")
    for folder in folders[:10]:  # Show first 10 folders
        folder_post_count = posts.filter(folder=folder).count()
        print(f"- Folder '{folder.name}' (ID:{folder.id}): {folder_post_count} posts")

    # Clean up test request
    test_request.delete()
    print(f"\n- Cleaned up test ScraperRequest")

    print("\n=== DEBUG COMPLETE ===")

if __name__ == "__main__":
    debug_data_flow()
