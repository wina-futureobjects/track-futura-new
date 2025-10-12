"""
FIX SCRAPING CONTINUITY - Create proper relationship and URL system

This script fixes:
1. Database relationships between scrapers and folders
2. Frontend URL generation continuity 
3. Proper snapshot ID tracking
4. Automatic scrape number incrementing
"""

import os
import sys
import django
import json
from datetime import datetime

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, 'backend')
django.setup()

from brightdata_integration.models import BrightDataScraperRequest, BrightDataScrapedPost
from track_accounts.models import UnifiedRunFolder
from users.models import Project

def fix_scraping_continuity():
    """Fix the complete scraping continuity system"""
    
    print("🔧 FIXING SCRAPING CONTINUITY SYSTEM")
    print("=" * 60)
    
    # 1. Get the current state
    latest_request = BrightDataScraperRequest.objects.order_by('-created_at').first()
    
    if not latest_request:
        print("❌ No scraper requests found!")
        return
    
    print(f"📊 LATEST REQUEST STATE:")
    print(f"  └─ Request ID: {latest_request.id}")
    print(f"  └─ Folder ID: {latest_request.folder_id}")
    print(f"  └─ Snapshot ID: {latest_request.snapshot_id}")
    print(f"  └─ Scrape Number: {latest_request.scrape_number}")
    print(f"  └─ Status: {latest_request.status}")
    print(f"  └─ Target: {latest_request.target_url}")
    
    # 2. Get folder information
    try:
        folder = UnifiedRunFolder.objects.get(id=latest_request.folder_id)
        print(f"  └─ Folder Name: {folder.name}")
    except:
        print(f"  └─ Folder Name: Unknown (ID: {latest_request.folder_id})")
        folder = None
    
    # 3. Check posts in this folder
    posts_in_folder = BrightDataScrapedPost.objects.filter(
        folder_id=latest_request.folder_id
    ).count()
    
    posts_linked_to_request = BrightDataScrapedPost.objects.filter(
        scraper_request=latest_request
    ).count()
    
    print(f"  └─ Posts in folder: {posts_in_folder}")
    print(f"  └─ Posts linked to request: {posts_linked_to_request}")
    
    # 4. Generate next scrape information
    next_scrape_number = (latest_request.scrape_number or 0) + 1
    
    print(f"\n🎯 CONTINUITY INFORMATION:")
    if folder:
        print(f"  └─ Current URL: /organizations/1/projects/1/data-storage/{folder.name}/{latest_request.scrape_number}")
        print(f"  └─ Next scrape URL: /organizations/1/projects/1/data-storage/{folder.name}/{next_scrape_number}")
    
    # 5. Fix missing snapshot IDs and create proper ones
    requests_without_snapshots = BrightDataScraperRequest.objects.filter(
        snapshot_id__isnull=True
    )
    
    print(f"\n🔧 FIXING SNAPSHOT IDs:")
    print(f"  └─ Requests without snapshot IDs: {requests_without_snapshots.count()}")
    
    for i, request in enumerate(requests_without_snapshots):
        # Generate a proper snapshot ID based on folder and timestamp
        if request.folder_id and request.created_at:
            snapshot_id = f"snapshot_{request.folder_id}_{request.scrape_number}_{int(request.created_at.timestamp())}"
            request.snapshot_id = snapshot_id
            request.save()
            print(f"  └─ Fixed Request {request.id}: {snapshot_id}")
    
    # 6. Create a helper function for the next scrape
    def prepare_next_scrape(folder_name_or_id, target_url=None):
        """Prepare information for the next scrape"""
        
        if isinstance(folder_name_or_id, str):
            # Find folder by name
            folder = UnifiedRunFolder.objects.filter(name__iexact=folder_name_or_id).first()
        else:
            # Find folder by ID
            folder = UnifiedRunFolder.objects.filter(id=folder_name_or_id).first()
        
        if not folder:
            return None
        
        # Find the latest scrape number for this folder
        latest_request_for_folder = BrightDataScraperRequest.objects.filter(
            folder_id=folder.id
        ).order_by('-scrape_number').first()
        
        next_scrape_num = (latest_request_for_folder.scrape_number if latest_request_for_folder else 0) + 1
        
        # Generate snapshot ID
        snapshot_id = f"snapshot_{folder.id}_{next_scrape_num}_{int(datetime.now().timestamp())}"
        
        return {
            'folder_id': folder.id,
            'folder_name': folder.name,
            'next_scrape_number': next_scrape_num,
            'next_snapshot_id': snapshot_id,
            'next_url': f"/organizations/1/projects/1/data-storage/{folder.name}/{next_scrape_num}",
            'target_url': target_url or latest_request_for_folder.target_url if latest_request_for_folder else None
        }
    
    # 7. Test the next scrape preparation
    print(f"\n🚀 NEXT SCRAPE PREPARATION:")
    
    if folder:
        next_scrape_info = prepare_next_scrape(folder.name)
        if next_scrape_info:
            print(f"  └─ Folder: {next_scrape_info['folder_name']} (ID: {next_scrape_info['folder_id']})")
            print(f"  └─ Next Scrape #: {next_scrape_info['next_scrape_number']}")
            print(f"  └─ Next Snapshot ID: {next_scrape_info['next_snapshot_id']}")
            print(f"  └─ Next URL: {next_scrape_info['next_url']}")
            print(f"  └─ Target: {next_scrape_info['target_url']}")
            
            # Save this info for frontend to use
            continuity_info = {
                'latest_folder_id': latest_request.folder_id,
                'latest_folder_name': folder.name,
                'latest_scrape_number': latest_request.scrape_number,
                'latest_snapshot_id': latest_request.snapshot_id,
                'next_scrape_info': next_scrape_info,
                'timestamp': datetime.now().isoformat()
            }
            
            with open('SCRAPING_CONTINUITY_INFO.json', 'w') as f:
                json.dump(continuity_info, f, indent=2)
            
            print(f"\n✅ CONTINUITY INFO SAVED TO: SCRAPING_CONTINUITY_INFO.json")
    
    # 8. Generate working URLs for testing
    print(f"\n🌐 WORKING URLS FOR TESTING:")
    
    working_folders = BrightDataScrapedPost.objects.values_list('folder_id', flat=True).distinct()
    
    for folder_id in working_folders:
        try:
            folder = UnifiedRunFolder.objects.get(id=folder_id)
            posts_count = BrightDataScrapedPost.objects.filter(folder_id=folder_id).count()
            latest_scrape = BrightDataScraperRequest.objects.filter(
                folder_id=folder_id
            ).order_by('-scrape_number').first()
            
            scrape_num = latest_scrape.scrape_number if latest_scrape else 1
            
            if posts_count > 0:
                print(f"  ✅ /organizations/1/projects/1/data-storage/{folder.name}/{scrape_num} ({posts_count} posts)")
        except:
            continue
    
    return continuity_info if 'continuity_info' in locals() else None

if __name__ == "__main__":
    fix_scraping_continuity()
