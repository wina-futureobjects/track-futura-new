import os
import sys
import django
import requests
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.brightdata_integration.models import (
    BrightDataScraperRequest, 
    BrightDataScrapedPost, 
    UnifiedRunFolder
)

def check_scraping_continuity():
    """Check the complete scraping workflow and database relationships"""
    
    print("🔍 CHECKING SCRAPING CONTINUITY & DATABASE RELATIONSHIPS")
    print("=" * 60)
    
    # Check latest scraper requests
    print("\n📊 LATEST SCRAPER REQUESTS:")
    latest_requests = BrightDataScraperRequest.objects.all().order_by('-created_at')[:5]
    
    for req in latest_requests:
        print(f"Request ID: {req.id}")
        print(f"  └─ Snapshot ID: {req.snapshot_id}")
        print(f"  └─ Status: {req.status}")
        print(f"  └─ Folder: {req.run_folder.name if req.run_folder else 'None'}")
        print(f"  └─ Created: {req.created_at}")
        
        # Check scraped posts for this request
        posts = BrightDataScrapedPost.objects.filter(
            scraper_request=req
        ).count()
        print(f"  └─ Posts scraped: {posts}")
        print()
    
    # Check latest folders
    print("📁 LATEST RUN FOLDERS:")
    latest_folders = UnifiedRunFolder.objects.all().order_by('-created_at')[:5]
    
    for folder in latest_folders:
        print(f"Folder ID: {folder.id} - '{folder.name}'")
        
        # Count requests for this folder
        requests_count = BrightDataScraperRequest.objects.filter(
            run_folder=folder
        ).count()
        
        # Count total posts for this folder
        total_posts = BrightDataScrapedPost.objects.filter(
            scraper_request__run_folder=folder
        ).count()
        
        print(f"  └─ Requests: {requests_count}")
        print(f"  └─ Total Posts: {total_posts}")
        print(f"  └─ Created: {folder.created_at}")
        print()
    
    # Check newest snapshot ID
    print("🆔 SNAPSHOT ID ANALYSIS:")
    latest_request = BrightDataScraperRequest.objects.order_by('-created_at').first()
    if latest_request:
        print(f"Latest Snapshot ID: {latest_request.snapshot_id}")
        print(f"Latest Request ID: {latest_request.id}")
        print(f"Associated Folder: {latest_request.run_folder.name if latest_request.run_folder else 'None'}")
    else:
        print("No scraper requests found!")
    
    # Check if there are any orphaned posts
    print("\n🔗 RELATIONSHIP INTEGRITY CHECK:")
    total_posts = BrightDataScrapedPost.objects.count()
    posts_with_requests = BrightDataScrapedPost.objects.filter(
        scraper_request__isnull=False
    ).count()
    
    print(f"Total Posts: {total_posts}")
    print(f"Posts with Request: {posts_with_requests}")
    print(f"Orphaned Posts: {total_posts - posts_with_requests}")
    
    # Generate correct frontend URLs
    print("\n🌐 CORRECT FRONTEND URLS:")
    working_folders = UnifiedRunFolder.objects.filter(
        brightdatascrapedpost__isnull=False
    ).distinct().order_by('-created_at')[:3]
    
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage"
    
    for folder in working_folders:
        posts_count = BrightDataScrapedPost.objects.filter(
            scraper_request__run_folder=folder
        ).count()
        
        if posts_count > 0:
            print(f"✅ {base_url}/job/{folder.id} - '{folder.name}' ({posts_count} posts)")
    
    return latest_request.snapshot_id if latest_request else None

if __name__ == "__main__":
    newest_snapshot = check_scraping_continuity()
    print(f"\n🎯 NEWEST SNAPSHOT ID FOR FRONTEND: {newest_snapshot}")