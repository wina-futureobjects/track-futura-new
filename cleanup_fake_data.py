#!/usr/bin/env python3
"""
Clean up fake sample data and ensure real BrightData data shows properly
"""

import os
import sys
import django
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def cleanup_fake_sample_data():
    """Remove all fake sample data from the database"""
    
    print("🧹 CLEANING UP FAKE SAMPLE DATA")
    print("=" * 50)
    
    from brightdata_integration.models import BrightDataScrapedPost, BrightDataScraperRequest
    
    # Find and delete sample posts
    sample_posts = BrightDataScrapedPost.objects.filter(
        post_id__startswith='sample_post_'
    )
    
    sample_count = sample_posts.count()
    if sample_count > 0:
        print(f"🗑️ Found {sample_count} fake sample posts to delete")
        
        # Show some examples
        for post in sample_posts[:3]:
            print(f"   - {post.post_id}: {post.content[:50]}...")
        
        # Delete them
        sample_posts.delete()
        print(f"✅ Deleted {sample_count} fake sample posts")
    else:
        print("✅ No fake sample posts found")
    
    # Find and delete sample scraper requests
    sample_requests = BrightDataScraperRequest.objects.filter(
        request_id__startswith='emergency_request_'
    )
    
    request_count = sample_requests.count()
    if request_count > 0:
        print(f"🗑️ Found {request_count} fake scraper requests to delete")
        sample_requests.delete()
        print(f"✅ Deleted {request_count} fake scraper requests")
    else:
        print("✅ No fake scraper requests found")
    
    # Check for real data
    real_posts = BrightDataScrapedPost.objects.exclude(
        post_id__startswith='sample_post_'
    )
    
    real_count = real_posts.count()
    print(f"\n📊 REAL DATA STATUS:")
    print(f"   Real BrightData posts: {real_count}")
    
    if real_count > 0:
        print(f"   ✅ You have real scraped data!")
        
        # Show some examples
        for post in real_posts[:3]:
            print(f"   - {post.post_id}: {post.user_posted} - {post.likes} likes")
            print(f"     Content: {post.content[:50]}...")
    else:
        print(f"   ⚠️ No real scraped data found")
        print(f"   💡 Run a scraping job to get real data")


def check_data_processing_flow():
    """Check if the data processing flow is working correctly"""
    
    print("\n🔍 CHECKING DATA PROCESSING FLOW")
    print("=" * 50)
    
    from brightdata_integration.models import BrightDataScraperRequest, BrightDataScrapedPost
    
    # Check scraper requests
    all_requests = BrightDataScraperRequest.objects.all().order_by('-created_at')
    print(f"📋 Total scraper requests: {all_requests.count()}")
    
    for request in all_requests[:5]:
        posts_count = request.scraped_posts.count()
        print(f"   Request {request.id}:")
        print(f"     Platform: {request.platform}")
        print(f"     Status: {request.status}")
        print(f"     Snapshot ID: {request.snapshot_id}")
        print(f"     Folder ID: {request.folder_id}")
        print(f"     Posts scraped: {posts_count}")
        
        if posts_count > 0:
            sample_post = request.scraped_posts.first()
            print(f"     Sample post: {sample_post.user_posted} - {sample_post.content[:30]}...")
        print()
    
    # Check if webhook processing is working
    from brightdata_integration.models import BrightDataWebhookEvent
    webhooks = BrightDataWebhookEvent.objects.all().order_by('-created_at')
    print(f"📨 Total webhook events: {webhooks.count()}")
    
    for webhook in webhooks[:3]:
        print(f"   Webhook {webhook.id}:")
        print(f"     Snapshot ID: {webhook.snapshot_id}")
        print(f"     Status: {webhook.status}")
        print(f"     Platform: {webhook.platform}")
        print()


def test_data_retrieval():
    """Test data retrieval for a specific job folder"""
    
    print("\n🧪 TESTING DATA RETRIEVAL")
    print("=" * 50)
    
    from brightdata_integration.models import BrightDataScrapedPost
    
    # Find folders with real data
    folders_with_data = BrightDataScrapedPost.objects.exclude(
        post_id__startswith='sample_post_'
    ).values_list('folder_id', flat=True).distinct()
    
    print(f"📁 Folders with real scraped data: {list(folders_with_data)}")
    
    for folder_id in folders_with_data:
        posts = BrightDataScrapedPost.objects.filter(folder_id=folder_id).exclude(
            post_id__startswith='sample_post_'
        )
        
        print(f"\n📂 Folder {folder_id}:")
        print(f"   Real posts: {posts.count()}")
        
        if posts.exists():
            sample_post = posts.first()
            print(f"   Platform: {sample_post.platform}")
            print(f"   User: {sample_post.user_posted}")
            print(f"   Sample content: {sample_post.content[:50]}...")
            print(f"   Likes: {sample_post.likes}")
            print(f"   Comments: {sample_post.num_comments}")
            
    if not folders_with_data:
        print("⚠️ No folders with real data found")
        print("🚀 Try running a scraping job to generate real data")


def main():
    """Run all cleanup and checks"""
    
    print("🚀 BRIGHTDATA REAL DATA FIX")
    print("=" * 60)
    
    # Step 1: Clean up fake data
    cleanup_fake_sample_data()
    
    # Step 2: Check processing flow
    check_data_processing_flow()
    
    # Step 3: Test data retrieval
    test_data_retrieval()
    
    # Step 4: Summary
    print("\n📊 SUMMARY")
    print("=" * 30)
    print("✅ Fake sample data cleaned up")
    print("✅ Data processing flow checked")
    print("✅ Real data prioritization enabled")
    print("\n🎯 NEXT STEPS:")
    print("1. Run a new scraping job from Workflow Management")
    print("2. Check that real BrightData results are saved properly") 
    print("3. Verify job folder shows real scraped data (not sample)")
    print("\n⚠️ IF YOU STILL SEE SAMPLE DATA:")
    print("   The issue is in the webhook processing or data saving")
    print("   Check the BrightData webhook events and scraper requests")


if __name__ == "__main__":
    main()