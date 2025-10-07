#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test Instagram scraper with simulated Apify webhook data"""
import os
import sys
import django
import requests
import json

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apify_integration.models import ApifyBatchJob, ApifyScraperRequest
from users.models import Project

# Sample Instagram data from Apify format
SAMPLE_INSTAGRAM_DATA = [
    {
        "id": "test_ig_1",
        "ownerUsername": "nike",
        "caption": "Just Do It. New collection dropping soon! #Nike #JustDoIt #Sportswear",
        "likesCount": 125430,
        "commentsCount": 2341,
        "timestamp": "2025-09-15T14:30:00Z",
        "url": "https://www.instagram.com/p/test_ig_1/",
        "type": "Image",
        "displayUrl": "https://instagram.com/image1.jpg",
        "videoUrl": None,
        "videoViewCount": 0,
        "ownerFullName": "Nike",
        "ownerId": "nike_123",
        "hashtags": ["Nike", "JustDoIt", "Sportswear"],
        "mentions": [],
        "alt": "Nike sportswear collection"
    },
    {
        "id": "test_ig_2",
        "ownerUsername": "nike",
        "caption": "Breaking barriers with every step. 🏃‍♀️ #Running #Athletes #NikeRunning",
        "likesCount": 98234,
        "commentsCount": 1876,
        "timestamp": "2025-09-14T10:15:00Z",
        "url": "https://www.instagram.com/p/test_ig_2/",
        "type": "Video",
        "displayUrl": "https://instagram.com/video_thumb.jpg",
        "videoUrl": "https://instagram.com/video.mp4",
        "videoViewCount": 452890,
        "ownerFullName": "Nike",
        "ownerId": "nike_123",
        "hashtags": ["Running", "Athletes", "NikeRunning"],
        "mentions": ["elonmusk"],
        "alt": ""
    },
    {
        "id": "test_ig_3",
        "ownerUsername": "adidas",
        "caption": "Impossible is Nothing. New Ultraboost 25 available now! #Adidas #Ultraboost",
        "likesCount": 87654,
        "commentsCount": 1543,
        "timestamp": "2025-09-13T16:45:00Z",
        "url": "https://www.instagram.com/p/test_ig_3/",
        "type": "Sidecar",
        "displayUrl": "https://instagram.com/carousel1.jpg",
        "videoUrl": None,
        "videoViewCount": 0,
        "ownerFullName": "Adidas",
        "ownerId": "adidas_456",
        "hashtags": ["Adidas", "Ultraboost"],
        "mentions": [],
        "alt": "Ultraboost 25 sneakers"
    }
]

def test_instagram_scraper():
    print("=" * 80)
    print("TESTING INSTAGRAM SCRAPER")
    print("=" * 80)

    # Step 1: Get or create project
    print("\n1. Getting test project...")
    project = Project.objects.first()
    if not project:
        print("   ❌ No project found. Please create a project first.")
        return False
    print(f"   Using project ID: {project.id}")

    # Step 2: Create a test batch job
    print("\n2. Creating test Instagram batch job...")
    batch_job = ApifyBatchJob.objects.create(
        name="Test Instagram Scrape - Nike & Adidas",
        project=project,
        platforms_to_scrape=["instagram"],
        content_types_to_scrape={"instagram": ["posts"]},
        status="processing"
    )
    print(f"   Created batch job ID: {batch_job.id}")

    # Step 3: Create ApifyConfig for Instagram
    print("\n3. Creating or getting Instagram Apify config...")
    from apify_integration.models import ApifyConfig
    from django.utils import timezone

    config, _ = ApifyConfig.objects.get_or_create(
        platform='instagram_posts',
        defaults={
            'name': 'Instagram Posts Scraper',
            'api_token': 'test_token',
            'actor_id': 'test_actor_id'
        }
    )
    print(f"   Using config ID: {config.id}")

    # Step 4: Create scraper request
    print("\n4. Creating scraper request...")
    scraper_request = ApifyScraperRequest.objects.create(
        config=config,
        batch_job=batch_job,
        platform='instagram',
        content_type='posts',
        target_url='https://www.instagram.com/nike/',
        source_name='nike',
        status='processing',
        started_at=timezone.now()
    )
    print(f"   Created scraper request ID: {scraper_request.id}")

    # Step 5: Process sample Instagram data directly
    print("\n5. Processing sample Instagram data...")

    # Import the processing function
    from apify_integration.views import _process_instagram_results

    # Process the results
    try:
        _process_instagram_results(scraper_request, SAMPLE_INSTAGRAM_DATA)
        print("   ✅ Instagram data processed successfully")
    except Exception as e:
        print(f"   ❌ Error processing Instagram data: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 6: Update batch job and scraper request status
    batch_job.status = "completed"
    batch_job.processed_sources = 2
    batch_job.successful_requests = len(SAMPLE_INSTAGRAM_DATA)
    batch_job.save()

    scraper_request.status = "completed"
    scraper_request.completed_at = timezone.now()
    scraper_request.save()
    print(f"\n6. Batch job marked as completed with {batch_job.successful_requests} results")

    # Step 7: Verify data was saved
    print("\n7. Verifying saved data...")
    from instagram_data.models import InstagramPost

    # Query posts by post_ids we created
    saved_post_ids = [post['id'] for post in SAMPLE_INSTAGRAM_DATA]
    saved_posts = InstagramPost.objects.filter(post_id__in=saved_post_ids)
    print(f"   Total posts saved: {saved_posts.count()}")

    if saved_posts.count() == len(SAMPLE_INSTAGRAM_DATA):
        print("   ✅ All posts saved successfully!")

        print("\n   Sample post details:")
        for post in saved_posts[:2]:
            print(f"   - User: {post.user_posted}")
            print(f"     Caption: {post.description[:60] if post.description else 'No caption'}...")
            print(f"     Likes: {post.likes}, Comments: {post.num_comments}")
            print(f"     Content Type: {post.content_type}")
            print(f"     Hashtags: {', '.join(post.hashtags) if post.hashtags else 'None'}")
            print()

        return True
    else:
        print(f"   ❌ Expected {len(SAMPLE_INSTAGRAM_DATA)} posts, but found {saved_posts.count()}")
        return False

if __name__ == "__main__":
    success = test_instagram_scraper()

    print("\n" + "=" * 80)
    if success:
        print("✅ INSTAGRAM SCRAPER TEST PASSED")
    else:
        print("❌ INSTAGRAM SCRAPER TEST FAILED")
    print("=" * 80)