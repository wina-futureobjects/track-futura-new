#!/usr/bin/env python3
"""
🔍 INSTAGRAM SNAPSHOT PROCESSOR
Process the Instagram snapshot s_lynh132v19n82v81kx using BrightData API
"""
import os
import sys
import django
import requests
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.models import BrightDataScraperRequest, BrightDataScrapedPost
from track_accounts.models import UnifiedRunFolder

def process_instagram_snapshot():
    print("🔍 INSTAGRAM SNAPSHOT PROCESSOR")
    print("=" * 50)
    
    # Instagram dataset info from your message
    dataset_id = "gd_lk5ns7kz21pck8jpis"  # Instagram dataset
    api_token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
    snapshot_id = "s_lynh132v19n82v81kx"  # Instagram snapshot
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }
    
    print(f"📋 INSTAGRAM SNAPSHOT DETAILS:")
    print(f"   Snapshot ID: {snapshot_id}")
    print(f"   Dataset: {dataset_id}")
    print(f"   Platform: Instagram")
    
    # Step 1: Check if already exists in database
    print(f"\n1️⃣ CHECKING DATABASE...")
    existing_request = BrightDataScraperRequest.objects.filter(
        snapshot_id=snapshot_id
    ).first()
    
    if existing_request:
        posts_count = BrightDataScrapedPost.objects.filter(
            scraper_request=existing_request
        ).count()
        print(f"   ✅ Found in database: Run {existing_request.id} with {posts_count} posts")
        print(f"   🌐 Frontend URL: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/run/{existing_request.id}")
        return existing_request.id
    
    # Step 2: Check progress
    print(f"\n2️⃣ CHECKING SNAPSHOT PROGRESS...")
    try:
        progress_url = f"https://api.brightdata.com/datasets/v3/progress/{snapshot_id}"
        progress_response = requests.get(progress_url, headers=headers, timeout=30)
        
        print(f"   Progress API: HTTP {progress_response.status_code}")
        if progress_response.status_code == 200:
            progress_data = progress_response.json()
            status = progress_data.get('status', 'unknown')
            print(f"   📊 Status: {status}")
            
            if status != 'ready':
                print(f"   ⏰ Snapshot not ready yet. Current status: {status}")
                print(f"   💡 Come back when status is 'ready'")
                return None
        else:
            print(f"   ⚠️  Progress check failed: {progress_response.text}")
    
    except Exception as e:
        print(f"   ⚠️  Progress check error: {e}")
    
    # Step 3: Download snapshot data
    print(f"\n3️⃣ DOWNLOADING SNAPSHOT DATA...")
    try:
        # Method 1: Direct snapshot download
        download_url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}"
        params = {"format": "json"}
        
        print(f"   📡 Downloading from: {download_url}")
        download_response = requests.get(download_url, headers=headers, params=params, timeout=60)
        
        print(f"   Download API: HTTP {download_response.status_code}")
        
        if download_response.status_code == 200:
            try:
                data = download_response.json()
                posts_data = data if isinstance(data, list) else [data]
                print(f"   ✅ Downloaded {len(posts_data)} Instagram posts")
                
                # Step 4: Create folder and scraper request
                print(f"\n4️⃣ CREATING DATABASE RECORDS...")
                
                folder_name = f"Instagram Data {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                folder = UnifiedRunFolder.objects.create(
                    name=folder_name,
                    description=f"Instagram data from BrightData snapshot {snapshot_id}",
                    category='social_media'
                )
                print(f"   ✅ Created folder: {folder.name} (ID: {folder.id})")
                
                scraper_request = BrightDataScraperRequest.objects.create(
                    platform='instagram',
                    target_url='instagram_api_import',
                    folder_id=folder.id,
                    snapshot_id=snapshot_id,
                    status='completed',
                    completed_at=datetime.now()
                )
                print(f"   ✅ Created scraper request: Run {scraper_request.id}")
                
                # Step 5: Process and save posts
                print(f"\n5️⃣ PROCESSING INSTAGRAM POSTS...")
                
                posts_created = 0
                for item in posts_data:
                    try:
                        # Instagram data mapping
                        post = BrightDataScrapedPost.objects.create(
                            scraper_request=scraper_request,
                            folder_id=folder.id,
                            post_id=item.get('id', item.get('shortcode', f'ig_post_{posts_created}')),
                            url=item.get('url', item.get('display_url', '')),
                            platform='instagram',
                            user_posted=item.get('owner', {}).get('username', item.get('username', 'Unknown')),
                            content=item.get('edge_media_to_caption', {}).get('edges', [{}])[0].get('node', {}).get('text', item.get('caption', '')),
                            description=item.get('accessibility_caption', ''),
                            likes=int(item.get('edge_liked_by', {}).get('count', item.get('likes', 0))),
                            num_comments=int(item.get('edge_media_to_comment', {}).get('count', item.get('comments', 0))),
                            date_posted=datetime.now(),
                            media_type=item.get('__typename', 'GraphImage').lower(),
                            media_url=item.get('display_url', ''),
                            is_verified=item.get('owner', {}).get('is_verified', False)
                        )
                        posts_created += 1
                        
                        if posts_created % 10 == 0:
                            print(f"   📝 Processed {posts_created} posts...")
                        
                    except Exception as e:
                        print(f"   ⚠️  Error creating post {posts_created}: {e}")
                        continue
                
                print(f"   ✅ Successfully created {posts_created} Instagram posts")
                
                # Step 6: Test endpoints
                print(f"\n6️⃣ TESTING ENDPOINTS...")
                
                # Test job-results endpoint
                try:
                    test_url = f"http://127.0.0.1:8000/api/brightdata/job-results/{folder.id}/"
                    test_response = requests.get(test_url, timeout=10)
                    if test_response.status_code == 200:
                        test_data = test_response.json()
                        print(f"   ✅ Local job-results: {test_data.get('total_results', 0)} posts")
                    else:
                        print(f"   ⚠️  Local job-results: HTTP {test_response.status_code}")
                except:
                    print(f"   ⚠️  Local server not running")
                
                # Production URLs
                print(f"\n🌐 ACCESS URLS:")
                print(f"   📱 Instagram Run: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/run/{scraper_request.id}")
                print(f"   📊 API Endpoint: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/job-results/{folder.id}/")
                
                return scraper_request.id
                
            except json.JSONDecodeError as e:
                print(f"   ❌ JSON decode error: {e}")
                print(f"   Raw response: {download_response.text[:200]}...")
                
        else:
            print(f"   ❌ Download failed: {download_response.status_code}")
            print(f"   Response: {download_response.text[:200]}...")
    
    except Exception as e:
        print(f"   ❌ Download error: {e}")
    
    return None

def get_snapshots_list():
    """Get list of all Instagram snapshots"""
    print(f"\n📋 GETTING INSTAGRAM SNAPSHOTS LIST...")
    
    dataset_id = "gd_lk5ns7kz21pck8jpis"
    api_token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        url = "https://api.brightdata.com/datasets/v3/snapshots"
        params = {
            "dataset_id": dataset_id,
            "status": "ready",
            "limit": 10
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        print(f"   Snapshots API: HTTP {response.status_code}")
        
        if response.status_code == 200:
            snapshots = response.json()
            if isinstance(snapshots, list):
                print(f"   ✅ Found {len(snapshots)} ready snapshots")
                for snapshot in snapshots[:5]:  # Show first 5
                    snapshot_id = snapshot.get('id', 'N/A')
                    created_at = snapshot.get('created_at', 'N/A')
                    print(f"   📊 {snapshot_id} - {created_at}")
                return snapshots
            else:
                print(f"   📊 Response: {snapshots}")
        else:
            print(f"   ❌ Failed: {response.text}")
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    return []

if __name__ == "__main__":
    print("🎯 INSTAGRAM BRIGHTDATA INTEGRATION")
    print("=" * 50)
    
    # Get snapshots list first
    snapshots = get_snapshots_list()
    
    # Process the specific snapshot
    result = process_instagram_snapshot()
    
    if result:
        print(f"\n🎉 SUCCESS!")
        print(f"✅ Instagram snapshot processed successfully")
        print(f"✅ Run ID: {result}")
        print(f"✅ Ready for frontend access")
    else:
        print(f"\n⚠️  PROCESSING INCOMPLETE")
        print(f"Check snapshot status or try again later")