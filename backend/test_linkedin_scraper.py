#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test LinkedIn scraper with simulated Apify webhook data"""
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

# Sample LinkedIn data from Apify format
SAMPLE_LINKEDIN_DATA = [
    {
        "postId": "test_li_1",
        "text": "Just Do It! 💪 At Nike, we believe in pushing boundaries and inspiring athletes worldwide. Check out our latest innovation in performance wear. #Nike #Innovation #Performance",
        "postUrl": "https://www.linkedin.com/posts/nike_test_li_1",
        "likesCount": 5420,
        "commentsCount": 234,
        "sharesCount": 187,
        "author": {
            "name": "Nike",
            "title": "Sportswear Company",
            "headline": "Bringing inspiration and innovation to every athlete in the world",
            "url": "https://www.linkedin.com/company/nike",
            "profilePicture": "https://linkedin.com/nike_profile.jpg"
        },
        "images": ["https://linkedin.com/image1.jpg"],
        "type": "company",
        "publishedDate": "2025-09-15T14:30:00Z"
    },
    {
        "postId": "test_li_2",
        "text": "Breaking barriers in sustainable manufacturing! 🌱 Our commitment to reducing carbon emissions while maintaining premium quality. Learn more about our sustainability journey. #Sustainability #Manufacturing #Nike",
        "postUrl": "https://www.linkedin.com/posts/nike_test_li_2",
        "likesCount": 4123,
        "commentsCount": 189,
        "sharesCount": 145,
        "author": {
            "name": "Nike",
            "title": "Sportswear Company",
            "headline": "Bringing inspiration and innovation to every athlete in the world",
            "url": "https://www.linkedin.com/company/nike",
            "profilePicture": "https://linkedin.com/nike_profile.jpg"
        },
        "videos": ["https://linkedin.com/video1.mp4"],
        "type": "company",
        "publishedDate": "2025-09-14T10:15:00Z"
    },
    {
        "postId": "test_li_3",
        "text": "Impossible is Nothing ⚽ Proud to announce our partnership with grassroots football programs across 50 countries. Building tomorrow's champions today. #Adidas #Football #Community",
        "postUrl": "https://www.linkedin.com/posts/adidas_test_li_3",
        "likesCount": 3876,
        "commentsCount": 156,
        "sharesCount": 98,
        "author": {
            "name": "Adidas",
            "title": "Sporting Goods Company",
            "headline": "Through sport, we have the power to change lives",
            "url": "https://www.linkedin.com/company/adidas",
            "profilePicture": "https://linkedin.com/adidas_profile.jpg"
        },
        "images": [
            "https://linkedin.com/image2.jpg",
            "https://linkedin.com/image3.jpg"
        ],
        "type": "company",
        "publishedDate": "2025-09-13T16:45:00Z"
    }
]

def test_linkedin_scraper():
    print("=" * 80)
    print("TESTING LINKEDIN SCRAPER")
    print("=" * 80)

    # Step 1: Get or create project
    print("\n1. Getting test project...")
    project = Project.objects.first()
    if not project:
        print("   ❌ No project found. Please create a project first.")
        return False
    print(f"   Using project ID: {project.id}")

    # Step 2: Create a test batch job
    print("\n2. Creating test LinkedIn batch job...")
    batch_job = ApifyBatchJob.objects.create(
        name="Test LinkedIn Scrape - Nike & Adidas",
        project=project,
        platforms_to_scrape=["linkedin"],
        content_types_to_scrape={"linkedin": ["posts"]},
        status="processing"
    )
    print(f"   Created batch job ID: {batch_job.id}")

    # Step 3: Create ApifyConfig for LinkedIn
    print("\n3. Creating or getting LinkedIn Apify config...")

    config, _ = ApifyConfig.objects.get_or_create(
        platform='linkedin_posts',
        defaults={
            'name': 'LinkedIn Posts Scraper',
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
        platform='linkedin',
        content_type='posts',
        target_url='https://www.linkedin.com/company/nike/',
        source_name='nike',
        status='processing',
        started_at=timezone.now()
    )
    print(f"   Created scraper request ID: {scraper_request.id}")

    # Step 5: Process sample LinkedIn data directly
    print("\n5. Processing sample LinkedIn data...")

    # Import the processing function
    from apify_integration.views import _process_linkedin_results

    # Process the results
    try:
        _process_linkedin_results(scraper_request, SAMPLE_LINKEDIN_DATA)
        print("   ✅ LinkedIn data processed successfully")
    except Exception as e:
        print(f"   ❌ Error processing LinkedIn data: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 6: Update batch job and scraper request status
    batch_job.status = "completed"
    batch_job.processed_sources = 2
    batch_job.successful_requests = len(SAMPLE_LINKEDIN_DATA)
    batch_job.save()

    scraper_request.status = "completed"
    scraper_request.completed_at = timezone.now()
    scraper_request.save()
    print(f"\n6. Batch job marked as completed with {batch_job.successful_requests} results")

    # Step 7: Verify data was saved
    print("\n7. Verifying saved data...")
    from linkedin_data.models import LinkedInPost

    # Query posts by post_ids we created
    saved_post_ids = [post['postId'] for post in SAMPLE_LINKEDIN_DATA]
    saved_posts = LinkedInPost.objects.filter(post_id__in=saved_post_ids)
    print(f"   Total posts saved: {saved_posts.count()}")

    if saved_posts.count() == len(SAMPLE_LINKEDIN_DATA):
        print("   ✅ All posts saved successfully!")

        print("\n   Sample post details:")
        for post in saved_posts[:2]:
            print(f"   - Author: {post.user_posted}")
            print(f"     Title: {post.user_title if post.user_title else 'No title'}")
            print(f"     Text: {post.description[:60] if post.description else 'No text'}...")
            print(f"     Likes: {post.likes}, Comments: {post.num_comments}, Shares: {post.num_shares}")
            print()

        return True
    else:
        print(f"   ❌ Expected {len(SAMPLE_LINKEDIN_DATA)} posts, but found {saved_posts.count()}")
        return False

if __name__ == "__main__":
    success = test_linkedin_scraper()

    print("\n" + "=" * 80)
    if success:
        print("✅ LINKEDIN SCRAPER TEST PASSED")
    else:
        print("❌ LINKEDIN SCRAPER TEST FAILED")
    print("=" * 80)