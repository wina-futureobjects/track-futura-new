#!/usr/bin/env python3
"""
🔍 PROCESS LATEST INSTAGRAM SNAPSHOT  
Process the most recent ready Instagram snapshot
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

def process_latest_instagram_snapshot():
    print("🔍 PROCESSING LATEST INSTAGRAM SNAPSHOT")
    print("=" * 50)
    
    # Instagram dataset info
    dataset_id = "gd_lk5ns7kz21pck8jpis"
    api_token = "8af6995e-3baa-4b69-9df7-8d7671e621eb"
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }
    
    # Step 1: Get list of ready snapshots
    print(f"1️⃣ GETTING READY SNAPSHOTS...")
    try:
        url = "https://api.brightdata.com/datasets/v3/snapshots"
        params = {
            "dataset_id": dataset_id,
            "status": "ready",
            "limit": 5
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        print(f"   Snapshots API: HTTP {response.status_code}")
        
        if response.status_code == 200:
            snapshots = response.json()
            if isinstance(snapshots, list) and len(snapshots) > 0:
                # Use the first (most recent) snapshot
                latest_snapshot = snapshots[0]
                snapshot_id = latest_snapshot.get('id')
                print(f"   ✅ Using latest snapshot: {snapshot_id}")
                
                # Check if already processed
                existing_request = BrightDataScraperRequest.objects.filter(
                    snapshot_id=snapshot_id
                ).first()
                
                if existing_request:
                    posts_count = BrightDataScrapedPost.objects.filter(
                        scraper_request=existing_request
                    ).count()
                    print(f"   ✅ Already processed: Run {existing_request.id} with {posts_count} posts")
                    print(f"   🌐 URL: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/run/{existing_request.id}")
                    return existing_request.id
                
                # Step 2: Download the snapshot
                print(f"\n2️⃣ DOWNLOADING SNAPSHOT {snapshot_id}...")
                
                download_url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}"
                download_params = {"format": "json"}
                
                download_response = requests.get(download_url, headers=headers, params=download_params, timeout=60)
                print(f"   Download: HTTP {download_response.status_code}")
                
                if download_response.status_code == 200:
                    try:
                        data = download_response.json()
                        posts_data = data if isinstance(data, list) else [data]
                        print(f"   ✅ Downloaded {len(posts_data)} Instagram posts")
                        
                        # Step 3: Create database records
                        print(f"\n3️⃣ CREATING DATABASE RECORDS...")
                        
                        folder_name = f"Instagram Scrape {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                        folder = UnifiedRunFolder.objects.create(
                            name=folder_name,
                            description=f"Latest Instagram data from BrightData",
                            category='social_media'
                        )
                        print(f"   ✅ Created folder: {folder.name} (ID: {folder.id})")
                        
                        scraper_request = BrightDataScraperRequest.objects.create(
                            platform='instagram',
                            target_url='instagram_latest_import',
                            folder_id=folder.id,
                            snapshot_id=snapshot_id,
                            status='completed',
                            completed_at=datetime.now()
                        )
                        print(f"   ✅ Created scraper request: Run {scraper_request.id}")
                        
                        # Step 4: Process posts
                        print(f"\n4️⃣ PROCESSING INSTAGRAM POSTS...")
                        
                        posts_created = 0
                        sample_posts = []
                        
                        for item in posts_data:
                            try:
                                # Extract Instagram post data
                                post_id = item.get('id', item.get('shortcode', f'ig_{posts_created}'))
                                url = item.get('url', item.get('display_url', ''))
                                
                                # Handle different Instagram API response formats
                                if 'owner' in item:
                                    username = item['owner'].get('username', 'Unknown')
                                    is_verified = item['owner'].get('is_verified', False)
                                else:
                                    username = item.get('username', item.get('user', 'Unknown'))
                                    is_verified = item.get('is_verified', False)
                                
                                # Handle caption/content
                                content = ''
                                if 'edge_media_to_caption' in item:
                                    edges = item['edge_media_to_caption'].get('edges', [])
                                    if edges:
                                        content = edges[0].get('node', {}).get('text', '')
                                else:
                                    content = item.get('caption', item.get('text', ''))
                                
                                # Handle engagement
                                likes = 0
                                if 'edge_liked_by' in item:
                                    likes = item['edge_liked_by'].get('count', 0)
                                else:
                                    likes = item.get('likes', item.get('like_count', 0))
                                
                                comments = 0
                                if 'edge_media_to_comment' in item:
                                    comments = item['edge_media_to_comment'].get('count', 0)
                                else:
                                    comments = item.get('comments', item.get('comment_count', 0))
                                
                                post = BrightDataScrapedPost.objects.create(
                                    scraper_request=scraper_request,
                                    folder_id=folder.id,
                                    post_id=post_id,
                                    url=url,
                                    platform='instagram',
                                    user_posted=username,
                                    content=content[:500],  # Limit content length
                                    description=item.get('accessibility_caption', '')[:200],
                                    likes=int(likes),
                                    num_comments=int(comments),
                                    date_posted=datetime.now(),
                                    media_type=item.get('__typename', 'post').lower(),
                                    media_url=item.get('display_url', ''),
                                    is_verified=is_verified
                                )
                                posts_created += 1
                                
                                # Collect sample for display
                                if len(sample_posts) < 3:
                                    sample_posts.append({
                                        'user': username,
                                        'content': content[:50] + '...' if len(content) > 50 else content,
                                        'likes': likes,
                                        'comments': comments
                                    })
                                
                                if posts_created % 10 == 0:
                                    print(f"   📝 Processed {posts_created} posts...")
                                
                            except Exception as e:
                                print(f"   ⚠️  Error creating post {posts_created}: {e}")
                                continue
                        
                        print(f"   ✅ Successfully created {posts_created} Instagram posts")
                        
                        # Show samples
                        if sample_posts:
                            print(f"\n📝 SAMPLE POSTS:")
                            for i, sample in enumerate(sample_posts, 1):
                                print(f"   {i}. @{sample['user']}: {sample['content']}")
                                print(f"      ❤️  {sample['likes']} likes, 💬 {sample['comments']} comments")
                        
                        # Step 5: Generate URLs
                        print(f"\n🌐 ACCESS URLS:")
                        print(f"   📱 Instagram Run: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/run/{scraper_request.id}")
                        print(f"   📊 API Endpoint: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/job-results/{folder.id}/")
                        
                        return scraper_request.id
                        
                    except json.JSONDecodeError as e:
                        print(f"   ❌ JSON error: {e}")
                        
                else:
                    print(f"   ❌ Download failed: {download_response.text}")
                    
            else:
                print(f"   ❌ No ready snapshots found")
        else:
            print(f"   ❌ API error: {response.text}")
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    return None

if __name__ == "__main__":
    result = process_latest_instagram_snapshot()
    
    if result:
        print(f"\n🎉 SUCCESS! Instagram data processed")
        print(f"✅ Run ID: {result}")
        print(f"✅ Ready for production access")
    else:
        print(f"\n❌ Processing failed")