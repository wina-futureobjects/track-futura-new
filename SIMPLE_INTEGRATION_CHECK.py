#!/usr/bin/env python3
"""
SIMPLE FIX: Check what's really happening with the scraping integration
Focus on the basic: scrape -> store -> display workflow
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

def check_simple_integration():
    """Check the basic scrape -> store -> display integration"""
    
    print("🔍 CHECKING BASIC INTEGRATION: SCRAPE -> STORE -> DISPLAY")
    print("=" * 80)
    
    # 1. Check latest folders created
    print("\n1️⃣ LATEST FOLDERS CREATED:")
    latest_folders = UnifiedRunFolder.objects.order_by('-created_at')[:10]
    
    for i, folder in enumerate(latest_folders, 1):
        post_count = BrightDataScrapedPost.objects.filter(folder_id=folder.id).count()
        request_count = BrightDataScraperRequest.objects.filter(folder_id=folder.id).count()
        
        print(f"   {i}. ID {folder.id}: '{folder.name}' ({folder.folder_type})")
        print(f"      Created: {folder.created_at}")
        print(f"      Posts: {post_count}, Requests: {request_count}")
        
        # Check if this should have the URL you're trying
        if folder.id in [278, 277, 276, 275, 274, 273, 272, 271]:
            print(f"      🎯 THIS COULD BE YOUR TARGET FOLDER!")
            
        print()
    
    # 2. Check latest scraper requests  
    print("\n2️⃣ LATEST SCRAPER REQUESTS:")
    latest_requests = BrightDataScraperRequest.objects.order_by('-created_at')[:10]
    
    for i, req in enumerate(latest_requests, 1):
        posts_count = BrightDataScrapedPost.objects.filter(scraper_request=req).count()
        print(f"   {i}. Request {req.id}: Folder {req.folder_id} - {req.platform}")
        print(f"      Status: {req.status} | Posts: {posts_count}")
        print(f"      Created: {req.created_at}")
        print()
    
    # 3. Check latest scraped posts
    print("\n3️⃣ LATEST SCRAPED POSTS:")
    latest_posts = BrightDataScrapedPost.objects.order_by('-created_at')[:10]
    
    for i, post in enumerate(latest_posts, 1):
        print(f"   {i}. Folder {post.folder_id}: {post.platform} by {post.user_posted}")
        print(f"      Content: {post.content[:50]}...")
        print(f"      Created: {post.created_at}")
        print()

def check_folder_278():
    """Specifically check if folder 278 exists"""
    
    print("\n🎯 CHECKING FOLDER 278 SPECIFICALLY:")
    print("=" * 80)
    
    try:
        folder_278 = UnifiedRunFolder.objects.get(id=278)
        print(f"✅ Folder 278 EXISTS: '{folder_278.name}' ({folder_278.folder_type})")
        print(f"   Created: {folder_278.created_at}")
        
        # Check data in this folder
        posts = BrightDataScrapedPost.objects.filter(folder_id=278)
        requests = BrightDataScraperRequest.objects.filter(folder_id=278)
        
        print(f"   Posts: {posts.count()}")
        print(f"   Requests: {requests.count()}")
        
        if posts.exists():
            sample_post = posts.first()
            print(f"   Sample post: {sample_post.platform} by {sample_post.user_posted}")
            
        # Show the working URL
        print(f"\n   🌐 WORKING URL: /organizations/1/projects/1/data-storage/run/{folder_278.id}")
        print(f"   🌐 API URL: /api/brightdata/job-results/{folder_278.id}/")
        
    except UnifiedRunFolder.DoesNotExist:
        print("❌ Folder 278 DOES NOT EXIST")
        print("   This is why your URL /data-storage/run/278 doesn't work!")
        
        # Find the actual highest folder
        highest_folder = UnifiedRunFolder.objects.order_by('-id').first()
        if highest_folder:
            print(f"   📊 Highest folder ID: {highest_folder.id} - '{highest_folder.name}'")
            print(f"   🌐 Try: /organizations/1/projects/1/data-storage/run/{highest_folder.id}")

def check_basic_workflow():
    """Check if the basic workflow is working"""
    
    print("\n⚙️ CHECKING BASIC WORKFLOW:")
    print("=" * 80)
    
    print("The workflow should be:")
    print("1. User triggers scrape → Creates UnifiedRunFolder")
    print("2. BrightData scrapes → Creates BrightDataScraperRequest") 
    print("3. BrightData sends data → Creates BrightDataScrapedPost records")
    print("4. Frontend shows data → Reads from BrightDataScrapedPost")
    print()
    
    # Check if each step is working
    total_folders = UnifiedRunFolder.objects.count()
    total_requests = BrightDataScraperRequest.objects.count()
    total_posts = BrightDataScrapedPost.objects.count()
    
    print(f"📊 WORKFLOW STATUS:")
    print(f"   Step 1 - Folders created: {total_folders} ✅" if total_folders > 0 else f"   Step 1 - Folders created: {total_folders} ❌")
    print(f"   Step 2 - Requests made: {total_requests} ✅" if total_requests > 0 else f"   Step 2 - Requests made: {total_requests} ❌")
    print(f"   Step 3 - Posts scraped: {total_posts} ✅" if total_posts > 0 else f"   Step 3 - Posts scraped: {total_posts} ❌")
    
    if total_posts > 0:
        print(f"   Step 4 - Display: Should work if URL is correct ✅")
    else:
        print(f"   Step 4 - Display: No data to show ❌")

if __name__ == "__main__":
    check_simple_integration()
    check_folder_278()
    check_basic_workflow()
    
    print("\n" + "=" * 80)
    print("🎯 SUMMARY:")
    print("1. If folder 278 exists: Integration is working, just need correct URL")
    print("2. If folder 278 missing: Frontend is generating wrong folder IDs") 
    print("3. If no recent data: Scraping process itself has issues")
    print("=" * 80)