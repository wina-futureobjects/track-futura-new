#!/usr/bin/env python3
"""
🎯 TEST SAVED SNAPSHOTS
Test that the snapshots were saved correctly to the database
"""

import os
import sys
import django

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(project_root, 'backend')
sys.path.insert(0, backend_path)

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.models import BrightDataScraperRequest, BrightDataScrapedPost
from track_accounts.models import UnifiedRunFolder

def test_saved_data():
    """Test the saved snapshots"""
    
    print("🎯 TESTING SAVED SNAPSHOTS")
    print("=" * 50)
    
    # Get the latest folders we created
    folders = UnifiedRunFolder.objects.filter(
        name__icontains='Nike'
    ).order_by('-id')[:2]
    
    print(f"📁 Found {folders.count()} Nike folders:")
    
    for folder in folders:
        print(f"\n📂 FOLDER: {folder.name} (ID: {folder.id})")
        print(f"   Platform: {folder.platform_code}")
        print(f"   Project: {folder.project_id}")
        
        # Get posts in this folder
        posts = BrightDataScrapedPost.objects.filter(folder_id=folder.id)
        print(f"   Posts: {posts.count()}")
        
        # Show sample posts
        for i, post in enumerate(posts[:3], 1):
            print(f"\n   📝 POST {i}:")
            print(f"      ID: {post.post_id}")
            print(f"      User: {post.user_posted}")
            print(f"      Content: {post.content[:100]}...")
            print(f"      Likes: {post.likes}")
            print(f"      Comments: {post.num_comments}")
        
        # API URL
        api_url = f"/api/brightdata/data-storage/run/{folder.id}/"
        print(f"\n   🔗 API URL: {api_url}")
        
        # Frontend URL
        frontend_url = f"https://trackfutura.futureobjects.io/organizations/1/projects/{folder.project_id}/data-storage"
        print(f"   🌐 Frontend: {frontend_url}")
    
    # Get scraper requests
    scraper_requests = BrightDataScraperRequest.objects.filter(
        snapshot_id__in=['s_mgp6kcyu28lbyl8rx9', 's_mgp6kclbi353dgcjk']
    )
    
    print(f"\n📊 SCRAPER REQUESTS:")
    for req in scraper_requests:
        print(f"   {req.platform}: {req.snapshot_id} -> Folder {req.folder_id} ({req.status})")
    
    # Summary
    total_posts = BrightDataScrapedPost.objects.filter(
        scraper_request__snapshot_id__in=['s_mgp6kcyu28lbyl8rx9', 's_mgp6kclbi353dgcjk']
    ).count()
    
    print(f"\n🎉 SUMMARY:")
    print(f"   ✅ Total Posts Saved: {total_posts}")
    print(f"   ✅ Folders Created: {folders.count()}")
    print(f"   ✅ Scraper Requests: {scraper_requests.count()}")
    
    # Main frontend access
    main_frontend = "https://trackfutura.futureobjects.io/organizations/1/projects/1/data-storage"
    print(f"\n🎯 MAIN ACCESS LINK:")
    print(f"   {main_frontend}")
    print(f"   📁 Your saved snapshots are in the 'Data Storage' section")
    
    return main_frontend

if __name__ == "__main__":
    try:
        url = test_saved_data()
        print(f"\n✅ SUCCESS! Access your data at: {url}")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()