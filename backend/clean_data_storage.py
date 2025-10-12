#!/usr/bin/env python3
"""
PRODUCTION DATA STORAGE CLEANER
Cleans ALL folders and posts from data storage only
"""
import os
import sys
import django

# Setup Django
sys.path.append('/app/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trackfutura.settings')
django.setup()

from brightdata_integration.models import UnifiedRunFolder, BrightDataScrapedPost, BrightDataScraperRequest

def clean_data_storage():
    """Clean all data storage folders and posts"""
    print("🧹 STARTING DATA STORAGE CLEANUP...")
    
    # Count before cleanup
    folders_count = UnifiedRunFolder.objects.count()
    posts_count = BrightDataScrapedPost.objects.count()
    requests_count = BrightDataScraperRequest.objects.count()
    
    print(f"📊 BEFORE CLEANUP:")
    print(f"   Folders: {folders_count}")
    print(f"   Posts: {posts_count}")
    print(f"   Scraper Requests: {requests_count}")
    
    # Delete all scraped posts
    print("🗑️  Deleting all scraped posts...")
    BrightDataScrapedPost.objects.all().delete()
    
    # Delete all folders
    print("🗑️  Deleting all folders...")
    UnifiedRunFolder.objects.all().delete()
    
    # Delete all scraper requests
    print("🗑️  Deleting all scraper requests...")
    BrightDataScraperRequest.objects.all().delete()
    
    # Verify cleanup
    folders_after = UnifiedRunFolder.objects.count()
    posts_after = BrightDataScrapedPost.objects.count()
    requests_after = BrightDataScraperRequest.objects.count()
    
    print(f"📊 AFTER CLEANUP:")
    print(f"   Folders: {folders_after}")
    print(f"   Posts: {posts_after}")
    print(f"   Scraper Requests: {requests_after}")
    
    if folders_after == 0 and posts_after == 0 and requests_after == 0:
        print("✅ SUCCESS! Data storage completely cleaned!")
        print("🚀 Ready for fresh scrape jobs!")
    else:
        print("❌ Cleanup incomplete - some items remain")
    
    return {
        'folders_deleted': folders_count - folders_after,
        'posts_deleted': posts_count - posts_after,
        'requests_deleted': requests_count - requests_after,
        'success': folders_after == 0 and posts_after == 0 and requests_after == 0
    }

if __name__ == '__main__':
    clean_data_storage()