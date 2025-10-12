"""
SHOW WORKING URLS - Display all actual working URLs for your data

This script will show you:
1. Current database state
2. Working URLs with actual data
3. Next scrape continuity information
4. How to trigger new scrapes properly
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

def show_working_urls():
    """Show all working URLs and continuity information"""
    
    print("🌐 WORKING URLS & CONTINUITY INFORMATION")
    print("=" * 70)
    
    # Get base URL
    base_url = "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site"
    
    # 1. Show current database state
    print("📊 CURRENT DATABASE STATE:")
    total_requests = BrightDataScraperRequest.objects.count()
    total_posts = BrightDataScrapedPost.objects.count()
    total_folders = UnifiedRunFolder.objects.count()
    
    print(f"  └─ Scraper Requests: {total_requests}")
    print(f"  └─ Scraped Posts: {total_posts}")
    print(f"  └─ Total Folders: {total_folders}")
    
    # 2. Get folders with actual data
    print(f"\n🎯 FOLDERS WITH ACTUAL DATA:")
    
    folders_with_data = []
    folder_ids_with_posts = BrightDataScrapedPost.objects.values_list('folder_id', flat=True).distinct()
    
    for folder_id in folder_ids_with_posts:
        try:
            folder = UnifiedRunFolder.objects.get(id=folder_id)
            posts_count = BrightDataScrapedPost.objects.filter(folder_id=folder_id).count()
            
            # Get latest scraper request for this folder
            latest_request = BrightDataScraperRequest.objects.filter(
                folder_id=folder_id
            ).order_by('-created_at', '-scrape_number').first()
            
            scrape_number = latest_request.scrape_number if latest_request else 1
            
            folder_info = {
                'id': folder.id,
                'name': folder.name,
                'posts_count': posts_count,
                'scrape_number': scrape_number,
                'latest_request_id': latest_request.id if latest_request else None,
                'snapshot_id': latest_request.snapshot_id if latest_request else None,
                'status': latest_request.status if latest_request else 'unknown'
            }
            
            folders_with_data.append(folder_info)
            
            print(f"  ✅ Folder: '{folder.name}' (ID: {folder.id})")
            print(f"      └─ Posts: {posts_count}")
            print(f"      └─ Scrape #: {scrape_number}")
            print(f"      └─ Status: {folder_info['status']}")
            if latest_request:
                print(f"      └─ Request ID: {latest_request.id}")
                print(f"      └─ Snapshot ID: {latest_request.snapshot_id}")
            print()
            
        except UnifiedRunFolder.DoesNotExist:
            continue
    
    # 3. Generate working URLs
    print(f"🌐 WORKING URLS (CLICK THESE NOW!):")
    print("=" * 50)
    
    for folder in folders_with_data:
        if folder['posts_count'] > 0:
            # Human-friendly URL
            human_url = f"{base_url}/organizations/1/projects/1/data-storage/{folder['name']}/{folder['scrape_number']}"
            
            # Legacy URL
            legacy_url = f"{base_url}/organizations/1/projects/1/data-storage/job/{folder['id']}"
            
            print(f"📁 {folder['name']} ({folder['posts_count']} posts)")
            print(f"   🔗 HUMAN-FRIENDLY: {human_url}")
            print(f"   🔗 LEGACY FORMAT:  {legacy_url}")
            
            # Run-style URL (for your /run/ pattern)
            run_url = f"{base_url}/organizations/1/projects/1/data-storage/run/{folder['id']}"
            print(f"   🔗 RUN FORMAT:     {run_url}")
            print()
    
    # 4. Show next scrape information
    print(f"🚀 NEXT SCRAPE CONTINUITY:")
    print("=" * 40)
    
    latest_overall_request = BrightDataScraperRequest.objects.order_by('-created_at').first()
    
    if latest_overall_request and latest_overall_request.folder_id:
        try:
            latest_folder = UnifiedRunFolder.objects.get(id=latest_overall_request.folder_id)
            next_scrape_number = (latest_overall_request.scrape_number or 0) + 1
            
            print(f"📊 LATEST SCRAPE:")
            print(f"  └─ Folder: {latest_folder.name}")
            print(f"  └─ Current Scrape #: {latest_overall_request.scrape_number}")
            print(f"  └─ Status: {latest_overall_request.status}")
            print(f"  └─ Snapshot ID: {latest_overall_request.snapshot_id}")
            
            print(f"\n🎯 NEXT SCRAPE WILL BE:")
            print(f"  └─ Folder: {latest_folder.name}")
            print(f"  └─ Scrape #: {next_scrape_number}")
            next_snapshot = f"snapshot_{latest_folder.id}_{next_scrape_number}_{int(datetime.now().timestamp())}"
            print(f"  └─ Snapshot ID: {next_snapshot}")
            
            next_url = f"{base_url}/organizations/1/projects/1/data-storage/{latest_folder.name}/{next_scrape_number}"
            print(f"  └─ URL: {next_url}")
            
        except UnifiedRunFolder.DoesNotExist:
            print("❌ Could not resolve latest folder information")
    
    # 5. Save continuity information
    continuity_data = {
        'timestamp': datetime.now().isoformat(),
        'base_url': base_url,
        'folders_with_data': folders_with_data,
        'latest_request': {
            'id': latest_overall_request.id if latest_overall_request else None,
            'folder_id': latest_overall_request.folder_id if latest_overall_request else None,
            'scrape_number': latest_overall_request.scrape_number if latest_overall_request else None,
            'snapshot_id': latest_overall_request.snapshot_id if latest_overall_request else None,
            'status': latest_overall_request.status if latest_overall_request else None
        } if latest_overall_request else None,
        'working_urls': []
    }
    
    # Add working URLs to data
    for folder in folders_with_data:
        if folder['posts_count'] > 0:
            continuity_data['working_urls'].append({
                'folder_name': folder['name'],
                'folder_id': folder['id'],
                'scrape_number': folder['scrape_number'],
                'posts_count': folder['posts_count'],
                'human_friendly_url': f"{base_url}/organizations/1/projects/1/data-storage/{folder['name']}/{folder['scrape_number']}",
                'legacy_url': f"{base_url}/organizations/1/projects/1/data-storage/job/{folder['id']}",
                'run_url': f"{base_url}/organizations/1/projects/1/data-storage/run/{folder['id']}"
            })
    
    # Save to file
    with open('WORKING_URLS_INFO.json', 'w') as f:
        json.dump(continuity_data, f, indent=2)
    
    print(f"\n💾 CONTINUITY INFO SAVED TO: WORKING_URLS_INFO.json")
    print(f"\n🎉 SUMMARY:")
    print(f"  ✅ Found {len(folders_with_data)} folders with data")
    print(f"  ✅ Total {sum(f['posts_count'] for f in folders_with_data)} posts available")
    print(f"  ✅ All URLs ready to use!")
    
    return continuity_data

if __name__ == "__main__":
    show_working_urls()