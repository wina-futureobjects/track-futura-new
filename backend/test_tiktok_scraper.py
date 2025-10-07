#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test TikTok scraper with simulated Apify webhook data"""
import os
import sys
import django

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apify_integration.models import ApifyBatchJob, ApifyScraperRequest, ApifyConfig
from users.models import Project
from django.utils import timezone

# Sample TikTok data from Apify format
SAMPLE_TIKTOK_DATA = [
    {
        "id": "test_tt_1",
        "text": "Just Do It 💪 #Nike #Fitness #Training #Motivation",
        "webVideoUrl": "https://www.tiktok.com/@nike/video/test_tt_1",
        "authorMeta": {
            "name": "nike",
            "fans": 5600000,
            "verified": True
        },
        "diggCount": 789000,
        "commentCount": 12000,
        "shareCount": 45000,
        "playCount": 8900000,
        "hashtags": [
            {"name": "Nike"},
            {"name": "Fitness"},
            {"name": "Training"},
            {"name": "Motivation"}
        ],
        "videoUrl": "https://tiktok.com/video1.mp4",
        "covers": {
            "default": "https://tiktok.com/cover1.jpg"
        },
        "musicMeta": {
            "musicName": "Motivational Beat"
        },
        "createTime": "2025-09-15T14:30:00Z"
    },
    {
        "id": "test_tt_2",
        "text": "New Air Max drop! 🔥 Link in bio #Nike #Sneakers #Fashion #Style",
        "webVideoUrl": "https://www.tiktok.com/@nike/video/test_tt_2",
        "authorMeta": {
            "name": "nike",
            "fans": 5600000,
            "verified": True
        },
        "diggCount": 654000,
        "commentCount": 9800,
        "shareCount": 32000,
        "playCount": 7200000,
        "hashtags": [
            {"name": "Nike"},
            {"name": "Sneakers"},
            {"name": "Fashion"},
            {"name": "Style"}
        ],
        "videoUrl": "https://tiktok.com/video2.mp4",
        "covers": {
            "default": "https://tiktok.com/cover2.jpg"
        },
        "musicMeta": {
            "musicName": "Hip Hop Beat"
        },
        "createTime": "2025-09-14T10:15:00Z"
    },
    {
        "id": "test_tt_3",
        "text": "Impossible is Nothing ⚽ #Adidas #Soccer #Football #Sports",
        "webVideoUrl": "https://www.tiktok.com/@adidas/video/test_tt_3",
        "authorMeta": {
            "name": "adidas",
            "fans": 4200000,
            "verified": True
        },
        "diggCount": 543000,
        "commentCount": 8500,
        "shareCount": 28000,
        "playCount": 6100000,
        "hashtags": [
            {"name": "Adidas"},
            {"name": "Soccer"},
            {"name": "Football"},
            {"name": "Sports"}
        ],
        "videoUrl": "https://tiktok.com/video3.mp4",
        "covers": {
            "default": "https://tiktok.com/cover3.jpg"
        },
        "musicMeta": {
            "musicName": "Sports Anthem"
        },
        "createTime": "2025-09-13T16:45:00Z"
    }
]

def test_tiktok_scraper():
    print("=" * 80)
    print("TESTING TIKTOK SCRAPER")
    print("=" * 80)

    # Step 1: Get or create project
    print("\n1. Getting test project...")
    project = Project.objects.first()
    if not project:
        print("   ❌ No project found. Please create a project first.")
        return False
    print(f"   Using project ID: {project.id}")

    # Step 2: Create a test batch job
    print("\n2. Creating test TikTok batch job...")
    batch_job = ApifyBatchJob.objects.create(
        name="Test TikTok Scrape - Nike & Adidas",
        project=project,
        platforms_to_scrape=["tiktok"],
        content_types_to_scrape={"tiktok": ["posts"]},
        status="processing"
    )
    print(f"   Created batch job ID: {batch_job.id}")

    # Step 3: Create ApifyConfig for TikTok
    print("\n3. Creating or getting TikTok Apify config...")

    config, _ = ApifyConfig.objects.get_or_create(
        platform='tiktok_posts',
        defaults={
            'name': 'TikTok Posts Scraper',
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
        platform='tiktok',
        content_type='posts',
        target_url='https://www.tiktok.com/@nike/',
        source_name='nike',
        status='processing',
        started_at=timezone.now()
    )
    print(f"   Created scraper request ID: {scraper_request.id}")

    # Step 5: Process sample TikTok data directly
    print("\n5. Processing sample TikTok data...")

    # Import the processing function
    from apify_integration.views import _process_tiktok_results

    # Process the results
    try:
        _process_tiktok_results(scraper_request, SAMPLE_TIKTOK_DATA)
        print("   ✅ TikTok data processed successfully")
    except Exception as e:
        print(f"   ❌ Error processing TikTok data: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 6: Update batch job and scraper request status
    batch_job.status = "completed"
    batch_job.processed_sources = 2
    batch_job.successful_requests = len(SAMPLE_TIKTOK_DATA)
    batch_job.save()

    scraper_request.status = "completed"
    scraper_request.completed_at = timezone.now()
    scraper_request.save()
    print(f"\n6. Batch job marked as completed with {batch_job.successful_requests} results")

    # Step 7: Verify data was saved
    print("\n7. Verifying saved data...")
    from tiktok_data.models import TikTokPost

    # Query posts by post_ids we created
    saved_post_ids = [post['id'] for post in SAMPLE_TIKTOK_DATA]
    saved_posts = TikTokPost.objects.filter(post_id__in=saved_post_ids)
    print(f"   Total posts saved: {saved_posts.count()}")

    if saved_posts.count() == len(SAMPLE_TIKTOK_DATA):
        print("   ✅ All posts saved successfully!")

        print("\n   Sample post details:")
        for post in saved_posts[:2]:
            print(f"   - User: @{post.user_posted}")
            print(f"     Description: {post.description[:60] if post.description else 'No description'}...")
            print(f"     Likes: {post.likes}, Comments: {post.num_comments}")
            print(f"     Hashtags: {post.hashtags if post.hashtags else 'None'}")
            print()

        return True
    else:
        print(f"   ❌ Expected {len(SAMPLE_TIKTOK_DATA)} posts, but found {saved_posts.count()}")
        return False

if __name__ == "__main__":
    success = test_tiktok_scraper()

    print("\n" + "=" * 80)
    if success:
        print("✅ TIKTOK SCRAPER TEST PASSED")
    else:
        print("❌ TIKTOK SCRAPER TEST FAILED")
    print("=" * 80)