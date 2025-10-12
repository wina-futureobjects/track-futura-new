#!/usr/bin/env python3
"""
🚀 BRIGHTDATA API INTEGRATION - Fetch latest snapshots and create run endpoints
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import requests
import json
from datetime import datetime
from brightdata_integration.models import BrightDataScraperRequest, BrightDataScrapedPost, BrightDataWebhookEvent
from track_accounts.models import UnifiedRunFolder

def fetch_brightdata_snapshots():
    print("🚀 BRIGHTDATA API INTEGRATION - FETCH LATEST DATA")
    print("=" * 60)
    
    # BrightData API config (from CEO message)
    dataset_id = "gd_lkaxegm826bjpoo9m5"
    api_token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }
    
    print(f"📋 BRIGHTDATA CONFIG:")
    print(f"   Dataset ID: {dataset_id}")
    print(f"   API Token: {api_token[:20]}...")
    
    # Fetch snapshots from BrightData API
    try:
        print(f"\n📡 FETCHING SNAPSHOTS FROM BRIGHTDATA...")
        url = f"https://api.brightdata.com/datasets/v3/snapshots"
        params = {
            "dataset_id": dataset_id,
            "status": "ready",
            "limit": 10
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        print(f"   API Response: {response.status_code}")
        
        if response.status_code == 200:
            snapshots = response.json()
            print(f"   ✅ Found {len(snapshots)} ready snapshots")
            
            for i, snapshot in enumerate(snapshots[:5]):
                snapshot_id = snapshot.get('id', 'unknown')
                status = snapshot.get('status', 'unknown')
                created = snapshot.get('created_at', 'unknown')
                print(f"   {i+1}. {snapshot_id} - {status} - {created}")
                
                # Check if we have this snapshot in database
                existing_request = BrightDataScraperRequest.objects.filter(
                    snapshot_id=snapshot_id
                ).first()
                
                if existing_request:
                    posts_count = BrightDataScrapedPost.objects.filter(
                        folder_id=existing_request.folder_id
                    ).count()
                    print(f"      └── DB: Run {existing_request.id}, Folder {existing_request.folder_id}, {posts_count} posts")
                else:
                    print(f"      └── ❌ Not in database - missing webhook data")
                    
                    # Try to fetch data for this snapshot
                    try:
                        print(f"      └── 🔄 Fetching data for snapshot {snapshot_id}...")
                        data_url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}"
                        data_response = requests.get(data_url, headers=headers, timeout=30)
                        
                        if data_response.status_code == 200:
                            data = data_response.json()
                            print(f"      └── ✅ Retrieved {len(data)} items")
                            
                            if data and len(data) > 0:
                                # Create a new scraper request and folder
                                print(f"      └── 🚀 Creating new run for snapshot {snapshot_id}")
                                
                                # Create new folder
                                folder_name = f"BrightData {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                                folder = UnifiedRunFolder.objects.create(
                                    name=folder_name,
                                    description=f"Auto-created from BrightData snapshot {snapshot_id}",
                                    category='social_media',
                                    platform='instagram'
                                )
                                
                                # Create scraper request
                                scraper_request = BrightDataScraperRequest.objects.create(
                                    platform='instagram',
                                    target_url='auto_import',
                                    folder_id=folder.id,
                                    snapshot_id=snapshot_id,
                                    status='completed',
                                    completed_at=datetime.now()
                                )
                                
                                # Create posts
                                posts_created = 0
                                for item in data[:50]:  # Limit to 50 posts
                                    BrightDataScrapedPost.objects.create(
                                        scraper_request=scraper_request,
                                        folder_id=folder.id,
                                        post_id=item.get('id', f'post_{posts_created}'),
                                        url=item.get('url', ''),
                                        platform='instagram',
                                        user_posted=item.get('user_posted', item.get('username', 'unknown')),
                                        content=item.get('content', item.get('caption', '')),
                                        likes=int(item.get('likes', 0)),
                                        num_comments=int(item.get('num_comments', item.get('comments', 0))),
                                        date_posted=datetime.now()
                                    )
                                    posts_created += 1
                                
                                print(f"      └── ✅ Created Run {scraper_request.id} with {posts_created} posts")
                                print(f"      └── 🌐 Access: /run/{scraper_request.id}")
                                
                        else:
                            print(f"      └── ❌ Failed to fetch snapshot data: {data_response.status_code}")
                            
                    except Exception as e:
                        print(f"      └── ❌ Error fetching snapshot data: {e}")
        else:
            print(f"   ❌ Failed to fetch snapshots: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ API Error: {e}")
    
    # Show current status
    print(f"\n📊 CURRENT DATABASE STATUS:")
    requests = BrightDataScraperRequest.objects.all().order_by('-created_at')[:10]
    
    for req in requests:
        posts_count = BrightDataScrapedPost.objects.filter(folder_id=req.folder_id).count()
        print(f"   /run/{req.id} → {req.status} → {posts_count} posts")
        print(f"   └── Snapshot: {req.snapshot_id}")
        print(f"   └── Folder: {req.folder_id}")
        
    print(f"\n✅ AVAILABLE RUN ENDPOINTS:")
    for req in requests[:5]:
        posts_count = BrightDataScrapedPost.objects.filter(folder_id=req.folder_id).count()
        if posts_count > 0:
            print(f"   🔗 /run/{req.id} → {posts_count} posts")
            print(f"   🌐 https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/run/{req.id}")

if __name__ == "__main__":
    fetch_brightdata_snapshots()