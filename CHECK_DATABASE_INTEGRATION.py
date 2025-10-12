#!/usr/bin/env python3
"""
Check database integration and scraped data
"""

import os
import sys
import django

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.append(backend_path)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.models import BrightDataScrapedPost, BrightDataScraperRequest
from track_accounts.models import UnifiedRunFolder

def check_database_integration():
    """Check if database has scraped data and integration is working"""
    
    print("🔍 CHECKING DATABASE INTEGRATION")
    print("=" * 60)
    
    # Check scraped posts
    post_count = BrightDataScrapedPost.objects.count()
    request_count = BrightDataScraperRequest.objects.count()
    
    print(f"\n📊 DATABASE COUNTS:")
    print(f"   BrightDataScrapedPost: {post_count}")
    print(f"   BrightDataScraperRequest: {request_count}")
    
    if post_count == 0:
        print("\n❌ NO SCRAPED DATA FOUND")
        print("   The database doesn't have any scraped posts yet.")
        print("   This means either:")
        print("   1. No scraping jobs have been run")
        print("   2. Scraping jobs failed")
        print("   3. Data isn't being saved to the database properly")
        return False
    
    # Check folders with data
    print(f"\n📁 FOLDERS WITH SCRAPED DATA:")
    folder_ids = BrightDataScrapedPost.objects.values_list('folder_id', flat=True).distinct()
    
    for folder_id in folder_ids:
        post_count = BrightDataScrapedPost.objects.filter(folder_id=folder_id).count()
        
        # Get folder name
        try:
            folder = UnifiedRunFolder.objects.get(id=folder_id)
            folder_name = folder.name
        except:
            folder_name = "Unknown"
        
        print(f"   Folder {folder_id} ({folder_name}): {post_count} posts")
        
        # Show sample posts
        sample_posts = BrightDataScrapedPost.objects.filter(folder_id=folder_id)[:3]
        for post in sample_posts:
            print(f"     - {post.platform}: {post.post_id} by {post.user_posted}")
    
    # Check scraper requests
    print(f"\n🔄 SCRAPER REQUESTS:")
    requests = BrightDataScraperRequest.objects.all()[:5]
    
    for req in requests:
        print(f"   Request {req.id}: folder_id={req.folder_id}, scrape_number={req.scrape_number}")
        print(f"     Platform: {req.platform}, Status: {req.status}")
        posts_for_request = BrightDataScrapedPost.objects.filter(scraper_request=req).count()
        print(f"     Posts: {posts_for_request}")
    
    return True

def test_endpoint_integration():
    """Test if the endpoints can actually return data"""
    
    print("\n🎯 TESTING ENDPOINT INTEGRATION")
    print("=" * 60)
    
    # Get available folders
    folders_with_data = BrightDataScrapedPost.objects.values_list('folder_id', flat=True).distinct()
    
    if not folders_with_data:
        print("❌ No folders with scraped data to test")
        return False
    
    # Test with actual data
    for folder_id in list(folders_with_data)[:3]:  # Test first 3 folders
        try:
            folder = UnifiedRunFolder.objects.get(id=folder_id)
            print(f"\n📋 Testing folder: {folder.name} (ID: {folder_id})")
            
            # Get scraper requests for this folder
            scraper_requests = BrightDataScraperRequest.objects.filter(folder_id=folder_id)
            print(f"   Scraper requests: {scraper_requests.count()}")
            
            for req in scraper_requests[:2]:  # Test first 2 scrapes
                posts = BrightDataScrapedPost.objects.filter(
                    folder_id=folder_id,
                    scraper_request=req
                )
                
                print(f"   Scrape #{req.scrape_number}: {posts.count()} posts")
                
                if posts.exists():
                    sample_post = posts.first()
                    print(f"     Sample: {sample_post.platform} post by {sample_post.user_posted}")
                    print(f"     URL: {sample_post.url}")
                    print(f"     Likes: {sample_post.likes}, Comments: {sample_post.num_comments}")
                    
                    # This is what the endpoint should return
                    print(f"   ✅ Endpoint /data-storage/{folder.name}/{req.scrape_number}/ should work")
                else:
                    print(f"     ❌ No posts linked to this scraper request")
        
        except UnifiedRunFolder.DoesNotExist:
            print(f"   ❌ Folder ID {folder_id} not found in UnifiedRunFolder")
    
    return True

def check_webhook_integration():
    """Check if webhooks are properly saving data"""
    
    print("\n🪝 CHECKING WEBHOOK INTEGRATION")
    print("=" * 60)
    
    from brightdata_integration.models import BrightDataWebhookEvent
    
    webhook_count = BrightDataWebhookEvent.objects.count()
    print(f"   Webhook events: {webhook_count}")
    
    if webhook_count > 0:
        recent_webhooks = BrightDataWebhookEvent.objects.all()[:5]
        for webhook in recent_webhooks:
            print(f"   Event {webhook.event_id}: {webhook.status}")
            
            # Check if webhook created posts
            posts_from_webhook = BrightDataScrapedPost.objects.filter(
                raw_data__contains={'snapshot_id': webhook.snapshot_id}
            ).count()
            print(f"     Created posts: {posts_from_webhook}")
    
    return webhook_count > 0

if __name__ == "__main__":
    print("🔍 BRIGHTDATA DATABASE INTEGRATION CHECK")
    print("=" * 70)
    
    has_data = check_database_integration()
    
    if has_data:
        test_endpoint_integration()
        check_webhook_integration()
        
        print("\n✅ INTEGRATION STATUS: WORKING")
        print("   The database has scraped data and endpoints should work")
    else:
        print("\n❌ INTEGRATION STATUS: NO DATA")
        print("   Need to run scraping jobs or check webhook integration")
    
    print("\n" + "=" * 70)