#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test Facebook scraper with simulated Apify webhook data"""
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

# Sample Facebook data from Apify format
SAMPLE_FACEBOOK_DATA = [
    {
        "postId": "test_fb_1",
        "text": "Just Do It! Check out our new Nike Air Max collection. Limited time offer! 👟 #Nike #Sneakers #Fashion",
        "user": "Nike Official",
        "likes": 245680,
        "comments": 4521,
        "shares": 8934,
        "views": 1234567,
        "postUrl": "https://www.facebook.com/nike/posts/test_fb_1",
        "timestamp": "2025-09-15T14:30:00Z",
        "profileUrl": "https://www.facebook.com/nike",
        "media": [
            {
                "type": "photo",
                "url": "https://facebook.com/photo1.jpg"
            }
        ]
    },
    {
        "postId": "test_fb_2",
        "text": "Breaking records with every step 🏃‍♀️ Meet our new running shoe technology that helps you go faster, longer. #RunningShoes #Athletics",
        "user": "Nike Official",
        "likes": 189234,
        "comments": 3234,
        "shares": 6543,
        "views": 987654,
        "postUrl": "https://www.facebook.com/nike/posts/test_fb_2",
        "timestamp": "2025-09-14T10:15:00Z",
        "profileUrl": "https://www.facebook.com/nike",
        "media": [
            {
                "type": "video",
                "url": "https://facebook.com/video1.mp4"
            }
        ]
    },
    {
        "postId": "test_fb_3",
        "text": "Impossible is Nothing ⚽ New Predator Edge launching tomorrow! Are you ready? #Adidas #Football #Soccer",
        "user": "Adidas",
        "likes": 156789,
        "comments": 2876,
        "shares": 5432,
        "views": 876543,
        "postUrl": "https://www.facebook.com/adidas/posts/test_fb_3",
        "timestamp": "2025-09-13T16:45:00Z",
        "profileUrl": "https://www.facebook.com/adidas",
        "media": [
            {
                "type": "photo",
                "url": "https://facebook.com/photo2.jpg"
            },
            {
                "type": "photo",
                "url": "https://facebook.com/photo3.jpg"
            }
        ]
    }
]

def test_facebook_scraper():
    print("=" * 80)
    print("TESTING FACEBOOK SCRAPER")
    print("=" * 80)

    # Step 1: Get or create project
    print("\n1. Getting test project...")
    project = Project.objects.first()
    if not project:
        print("   ❌ No project found. Please create a project first.")
        return False
    print(f"   Using project ID: {project.id}")

    # Step 2: Create a test batch job
    print("\n2. Creating test Facebook batch job...")
    batch_job = ApifyBatchJob.objects.create(
        name="Test Facebook Scrape - Nike & Adidas",
        project=project,
        platforms_to_scrape=["facebook"],
        content_types_to_scrape={"facebook": ["posts"]},
        status="processing"
    )
    print(f"   Created batch job ID: {batch_job.id}")

    # Step 3: Create ApifyConfig for Facebook
    print("\n3. Creating or getting Facebook Apify config...")

    config, _ = ApifyConfig.objects.get_or_create(
        platform='facebook_posts',
        defaults={
            'name': 'Facebook Posts Scraper',
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
        platform='facebook',
        content_type='posts',
        target_url='https://www.facebook.com/nike/',
        source_name='nike',
        status='processing',
        started_at=timezone.now()
    )
    print(f"   Created scraper request ID: {scraper_request.id}")

    # Step 5: Process sample Facebook data directly
    print("\n5. Processing sample Facebook data...")

    # Import the processing function
    from apify_integration.views import _process_facebook_results

    # Process the results
    try:
        _process_facebook_results(scraper_request, SAMPLE_FACEBOOK_DATA)
        print("   ✅ Facebook data processed successfully")
    except Exception as e:
        print(f"   ❌ Error processing Facebook data: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 6: Update batch job and scraper request status
    batch_job.status = "completed"
    batch_job.processed_sources = 2
    batch_job.successful_requests = len(SAMPLE_FACEBOOK_DATA)
    batch_job.save()

    scraper_request.status = "completed"
    scraper_request.completed_at = timezone.now()
    scraper_request.save()
    print(f"\n6. Batch job marked as completed with {batch_job.successful_requests} results")

    # Step 7: Verify data was saved
    print("\n7. Verifying saved data...")
    from facebook_data.models import FacebookPost

    # Query posts by post_ids we created
    saved_post_ids = [post['postId'] for post in SAMPLE_FACEBOOK_DATA]
    saved_posts = FacebookPost.objects.filter(post_id__in=saved_post_ids)
    print(f"   Total posts saved: {saved_posts.count()}")

    if saved_posts.count() == len(SAMPLE_FACEBOOK_DATA):
        print("   ✅ All posts saved successfully!")

        print("\n   Sample post details:")
        for post in saved_posts[:2]:
            print(f"   - User: {post.user_posted}")
            print(f"     Text: {post.content[:60] if post.content else 'No text'}...")
            print(f"     Likes: {post.likes}, Comments: {post.num_comments}, Shares: {post.num_shares}")
            print(f"     Views: {post.video_view_count}")
            print()

        return True
    else:
        print(f"   ❌ Expected {len(SAMPLE_FACEBOOK_DATA)} posts, but found {saved_posts.count()}")
        return False

if __name__ == "__main__":
    success = test_facebook_scraper()

    print("\n" + "=" * 80)
    if success:
        print("✅ FACEBOOK SCRAPER TEST PASSED")
    else:
        print("❌ FACEBOOK SCRAPER TEST FAILED")
    print("=" * 80)