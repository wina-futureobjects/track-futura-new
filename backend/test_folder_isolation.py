#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test that folders are properly isolated and don't show each other's data"""
import os
import sys
import django
import time

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apify_integration.models import ApifyBatchJob, ApifyScraperRequest, ApifyConfig
from apify_integration.views import _get_platform_results
from users.models import Project
from django.utils import timezone
from datetime import timedelta

def test_folder_isolation():
    print("=" * 80)
    print("TESTING FOLDER ISOLATION")
    print("=" * 80)

    # Step 1: Get project
    print("\n1. Getting test project...")
    project = Project.objects.first()
    if not project:
        print("   ❌ No project found. Please create a project first.")
        return False
    print(f"   Using project ID: {project.id}")

    # Step 2: Create batch job
    print("\n2. Creating test batch job...")
    batch_job = ApifyBatchJob.objects.create(
        name="Folder Isolation Test",
        project=project,
        platforms_to_scrape=["instagram"],
        content_types_to_scrape={"instagram": ["posts"]},
        status="processing"
    )
    print(f"   Created batch job ID: {batch_job.id}")

    # Step 3: Get or create Apify config
    print("\n3. Getting Instagram Apify config...")
    config, _ = ApifyConfig.objects.get_or_create(
        platform='instagram_posts',
        defaults={
            'name': 'Instagram Posts Scraper',
            'api_token': 'test_token',
            'actor_id': 'test_actor_id'
        }
    )

    # Step 4: Create FIRST scraper request with Nike data
    print("\n4. Creating FIRST scraper request for Nike...")
    scraper_request_1 = ApifyScraperRequest.objects.create(
        config=config,
        batch_job=batch_job,
        platform='instagram',
        content_type='posts',
        target_url='https://www.instagram.com/nike/',
        source_name='nike',
        status='processing',
        started_at=timezone.now()
    )
    print(f"   Created scraper request 1 ID: {scraper_request_1.id}")
    print(f"   Folder name will be: {batch_job.name} - Instagram Posts - {scraper_request_1.started_at.strftime('%Y-%m-%d %H:%M')}")

    # Sample Nike data
    nike_data = [
        {
            "id": "nike_post_1",
            "ownerUsername": "nike",
            "caption": "Nike Post 1 - Just Do It! #Nike",
            "likesCount": 100000,
            "commentsCount": 1000,
            "timestamp": "2025-09-15T14:30:00Z",
            "url": "https://www.instagram.com/p/nike_post_1/",
            "type": "Image",
            "displayUrl": "https://instagram.com/nike1.jpg"
        },
        {
            "id": "nike_post_2",
            "ownerUsername": "nike",
            "caption": "Nike Post 2 - New Collection! #Nike",
            "likesCount": 95000,
            "commentsCount": 900,
            "timestamp": "2025-09-15T15:00:00Z",
            "url": "https://www.instagram.com/p/nike_post_2/",
            "type": "Image",
            "displayUrl": "https://instagram.com/nike2.jpg"
        }
    ]

    # Process Nike data
    print("\n5. Processing Nike data...")
    from apify_integration.views import _process_instagram_results
    try:
        _process_instagram_results(scraper_request_1, nike_data)
        scraper_request_1.status = "completed"
        scraper_request_1.completed_at = timezone.now()
        scraper_request_1.save()
        print("   ✅ Nike data processed successfully")
    except Exception as e:
        print(f"   ❌ Error processing Nike data: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Wait a bit to ensure different timestamp
    print("\n6. Waiting 2 seconds to ensure different timestamp...")
    time.sleep(2)

    # Step 6: Create SECOND scraper request with Adidas data
    print("\n7. Creating SECOND scraper request for Adidas...")
    scraper_request_2 = ApifyScraperRequest.objects.create(
        config=config,
        batch_job=batch_job,
        platform='instagram',
        content_type='posts',
        target_url='https://www.instagram.com/adidas/',
        source_name='adidas',
        status='processing',
        started_at=timezone.now()
    )
    print(f"   Created scraper request 2 ID: {scraper_request_2.id}")
    print(f"   Folder name will be: {batch_job.name} - Instagram Posts - {scraper_request_2.started_at.strftime('%Y-%m-%d %H:%M')}")

    # Sample Adidas data
    adidas_data = [
        {
            "id": "adidas_post_1",
            "ownerUsername": "adidas",
            "caption": "Adidas Post 1 - Impossible is Nothing! #Adidas",
            "likesCount": 80000,
            "commentsCount": 800,
            "timestamp": "2025-09-15T14:30:00Z",
            "url": "https://www.instagram.com/p/adidas_post_1/",
            "type": "Image",
            "displayUrl": "https://instagram.com/adidas1.jpg"
        },
        {
            "id": "adidas_post_2",
            "ownerUsername": "adidas",
            "caption": "Adidas Post 2 - New Ultraboost! #Adidas",
            "likesCount": 75000,
            "commentsCount": 700,
            "timestamp": "2025-09-15T15:00:00Z",
            "url": "https://www.instagram.com/p/adidas_post_2/",
            "type": "Image",
            "displayUrl": "https://instagram.com/adidas2.jpg"
        }
    ]

    # Process Adidas data
    print("\n8. Processing Adidas data...")
    try:
        _process_instagram_results(scraper_request_2, adidas_data)
        scraper_request_2.status = "completed"
        scraper_request_2.completed_at = timezone.now()
        scraper_request_2.save()
        print("   ✅ Adidas data processed successfully")
    except Exception as e:
        print(f"   ❌ Error processing Adidas data: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 7: Verify isolation
    print("\n9. Verifying folder isolation...")

    # Get results for Nike folder (scraper_request_1)
    print("\n   9a. Getting Nike folder results...")
    nike_results = _get_platform_results(scraper_request_1)
    print(f"      Nike folder has {len(nike_results)} posts")

    # Get results for Adidas folder (scraper_request_2)
    print("\n   9b. Getting Adidas folder results...")
    adidas_results = _get_platform_results(scraper_request_2)
    print(f"      Adidas folder has {len(adidas_results)} posts")

    # Check isolation
    success = True

    # Verify Nike folder only has Nike posts
    print("\n   9c. Verifying Nike folder only has Nike posts...")
    if len(nike_results) != 2:
        print(f"      ❌ Expected 2 Nike posts, but found {len(nike_results)}")
        success = False
    else:
        nike_users = [post['user_posted'] for post in nike_results]
        if all(user == 'nike' for user in nike_users):
            print(f"      ✅ Nike folder contains only Nike posts: {nike_users}")
        else:
            print(f"      ❌ Nike folder contains posts from: {nike_users}")
            success = False

    # Verify Adidas folder only has Adidas posts
    print("\n   9d. Verifying Adidas folder only has Adidas posts...")
    if len(adidas_results) != 2:
        print(f"      ❌ Expected 2 Adidas posts, but found {len(adidas_results)}")
        success = False
    else:
        adidas_users = [post['user_posted'] for post in adidas_results]
        if all(user == 'adidas' for user in adidas_users):
            print(f"      ✅ Adidas folder contains only Adidas posts: {adidas_users}")
        else:
            print(f"      ❌ Adidas folder contains posts from: {adidas_users}")
            success = False

    # Verify no overlap
    print("\n   9e. Verifying no post overlap between folders...")
    nike_post_ids = [post['post_id'] for post in nike_results]
    adidas_post_ids = [post['post_id'] for post in adidas_results]
    overlap = set(nike_post_ids) & set(adidas_post_ids)

    if len(overlap) == 0:
        print(f"      ✅ No overlap between folders")
    else:
        print(f"      ❌ Found {len(overlap)} overlapping posts: {overlap}")
        success = False

    # Update batch job status
    batch_job.status = "completed"
    batch_job.successful_requests = 2
    batch_job.save()

    return success

if __name__ == "__main__":
    success = test_folder_isolation()

    print("\n" + "=" * 80)
    if success:
        print("✅ FOLDER ISOLATION TEST PASSED")
        print("   Each folder contains only its own data!")
    else:
        print("❌ FOLDER ISOLATION TEST FAILED")
        print("   Folders are showing each other's data!")
    print("=" * 80)