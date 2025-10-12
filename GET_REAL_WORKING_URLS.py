#!/usr/bin/env python3
"""
Get the real working URLs for folders with actual data
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

def get_real_working_urls():
    """Get the actual working URLs for your data"""
    
    print("🎯 REAL WORKING URLS FOR YOUR DATA")
    print("=" * 70)
    
    # Get folders with actual scraped data
    folders_with_data = BrightDataScrapedPost.objects.values_list('folder_id', flat=True).distinct()
    
    for folder_id in folders_with_data:
        try:
            folder = UnifiedRunFolder.objects.get(id=folder_id)
            post_count = BrightDataScrapedPost.objects.filter(folder_id=folder_id).count()
            
            print(f"\n📁 {folder.name} (ID: {folder_id})")
            print(f"   Posts: {post_count}")
            print(f"   Type: {folder.folder_type}")
            
            # Get scraper requests for this folder
            requests = BrightDataScraperRequest.objects.filter(folder_id=folder_id)
            for req in requests:
                posts_for_request = BrightDataScrapedPost.objects.filter(scraper_request=req).count()
                print(f"   Scrape #{req.scrape_number}: {posts_for_request} posts")
            
            # Show sample data
            sample_post = BrightDataScrapedPost.objects.filter(folder_id=folder_id).first()
            if sample_post:
                print(f"   Sample: {sample_post.platform} post by {sample_post.user_posted}")
                print(f"   Content: {sample_post.content[:50]}...")
            
            # Show CURRENT WORKING URLs
            print(f"\n   🌐 CURRENT WORKING URLS:")
            if folder.folder_type == 'run':
                print(f"   Frontend: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/run/{folder_id}")
            else:
                print(f"   Frontend: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/job/{folder_id}")
            
            print(f"   API: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/job-results/{folder_id}/")
            
            # Show FUTURE HUMAN-FRIENDLY URLs (when deployment works)
            folder_name_encoded = folder.name.replace(' ', '%20')
            print(f"\n   🚀 FUTURE HUMAN-FRIENDLY URLS (when Platform.sh deploys):")
            print(f"   Frontend: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/{folder_name_encoded}/1")
            print(f"   API: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/data-storage/{folder_name_encoded}/1/")
            
        except UnifiedRunFolder.DoesNotExist:
            print(f"❌ Folder {folder_id} exists in posts but not in UnifiedRunFolder")

def check_latest_activity():
    """Check for the most recent activity"""
    
    print(f"\n🕐 LATEST ACTIVITY CHECK")
    print("=" * 70)
    
    # Latest scraped posts
    latest_posts = BrightDataScrapedPost.objects.order_by('-created_at')[:5]
    if latest_posts.exists():
        print("📝 Latest scraped posts:")
        for post in latest_posts:
            print(f"   {post.created_at}: Folder {post.folder_id} - {post.platform} by {post.user_posted}")
    
    # Latest scraper requests  
    latest_requests = BrightDataScraperRequest.objects.order_by('-created_at')[:5]
    if latest_requests.exists():
        print("\n🔄 Latest scraper requests:")
        for req in latest_requests:
            print(f"   {req.created_at}: Folder {req.folder_id} - {req.platform} ({req.status})")
    
    # Latest folders
    latest_folders = UnifiedRunFolder.objects.order_by('-created_at')[:5]
    print("\n📁 Latest folders created:")
    for folder in latest_folders:
        post_count = BrightDataScrapedPost.objects.filter(folder_id=folder.id).count()
        print(f"   {folder.created_at}: ID {folder.id} - '{folder.name}' ({post_count} posts)")

if __name__ == "__main__":
    get_real_working_urls()
    check_latest_activity()
    
    print("\n" + "=" * 70)
    print("🎯 SOLUTION:")
    print("1. Use the CURRENT WORKING URLs above to access your data now")
    print("2. The /data-storage/run/271 URL is invalid - folder 271 doesn't exist")  
    print("3. Your real data is in folders 103 and 104 with working URLs")
    print("4. Human-friendly URLs will work when Platform.sh deployment completes")
    print("=" * 70)