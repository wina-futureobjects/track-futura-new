#!/usr/bin/env python3
"""
🎯 SIMPLE BRIGHTDATA SNAPSHOT SAVER
Save snapshots with only existing database columns
"""

import os
import sys
import json
import django
from datetime import datetime

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(project_root, 'backend')
sys.path.insert(0, backend_path)

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Now we can import Django models
from brightdata_integration.models import (
    BrightDataScraperRequest, 
    BrightDataScrapedPost, 
    BrightDataWebhookEvent
)
from track_accounts.models import UnifiedRunFolder
from users.models import Project
from django.utils import timezone

def save_snapshots_simple():
    """Save snapshots with minimal fields to avoid database issues"""
    
    print("🎯 SIMPLE BRIGHTDATA SNAPSHOT SAVER")
    print("=" * 50)
    
    # Your latest 2 snapshot files
    snapshot_files = [
        {
            'data_file': 'snapshot_s_mgp6kcyu28lbyl8rx9_data_20251013_214727.json',
            'snapshot_id': 's_mgp6kcyu28lbyl8rx9',
            'platform': 'facebook',
            'source': 'Nike Facebook'
        },
        {
            'data_file': 'snapshot_s_mgp6kclbi353dgcjk_data_20251013_214729.json',
            'snapshot_id': 's_mgp6kclbi353dgcjk',
            'platform': 'instagram',
            'source': 'Nike Instagram'
        }
    ]
    
    results = []
    
    for i, snapshot_info in enumerate(snapshot_files, 1):
        print(f"\n📊 PROCESSING SNAPSHOT {i}: {snapshot_info['snapshot_id']}")
        
        data_file = snapshot_info['data_file']
        
        if not os.path.exists(data_file):
            print(f"❌ Data file not found: {data_file}")
            continue
            
        # Load JSONL data
        posts_data = []
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line:
                        try:
                            post_obj = json.loads(line)
                            posts_data.append(post_obj)
                        except json.JSONDecodeError:
                            print(f"⚠️ Skipping invalid JSON at line {line_num}")
                            continue
            
            print(f"✅ Loaded {len(posts_data)} posts from {data_file}")
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            continue
        
        # Get or create project
        project, created = Project.objects.get_or_create(
            id=1,
            defaults={
                'name': 'TrackFutura Social Media',
                'description': 'BrightData snapshots'
            }
        )
        
        # Create folder
        folder_name = f"{snapshot_info['source']} Snapshot"
        folder = UnifiedRunFolder.objects.create(
            name=folder_name,
            project_id=project.id,
            folder_type='job',
            platform_code=snapshot_info['platform'],
            description=f"BrightData snapshot {snapshot_info['snapshot_id']}"
        )
        
        print(f"✅ Created folder: {folder.name} (ID: {folder.id})")
        
        # Create scraper request
        scraper_request = BrightDataScraperRequest.objects.create(
            snapshot_id=snapshot_info['snapshot_id'],
            platform=snapshot_info['platform'],
            target_url=f"BrightData {snapshot_info['snapshot_id']}",
            source_name=snapshot_info['source'],
            folder_id=folder.id,
            status='completed',
            scrape_number=1,
            completed_at=timezone.now()
        )
        
        print(f"✅ Created scraper request: {scraper_request.id}")
        
        # Process posts with minimal fields
        posts_created = 0
        posts_failed = 0
        
        for post_idx, post_data in enumerate(posts_data, 1):
            try:
                # Extract basic info based on platform
                if snapshot_info['platform'] == 'facebook':
                    post_id = post_data.get('post_id', f"fb_{folder.id}_{post_idx}")
                    url = post_data.get('url', '')
                    user_posted = post_data.get('user_username_raw', 'unknown')
                    content = post_data.get('content', '')
                    likes = int(post_data.get('num_likes_type', {}).get('num', 0))
                    num_comments = int(post_data.get('num_comments', 0))
                    shares = int(post_data.get('num_shares', 0))
                else:  # Instagram
                    post_id = post_data.get('post_id', f"ig_{folder.id}_{post_idx}")
                    url = post_data.get('url', '')
                    user_posted = post_data.get('user_posted', 'unknown')
                    content = post_data.get('description', '')
                    likes = int(post_data.get('likes_count', 0))
                    num_comments = int(post_data.get('comments_count', 0))
                    shares = 0
                
                # Create post with minimal required fields only
                BrightDataScrapedPost.objects.create(
                    post_id=post_id,
                    platform=snapshot_info['platform'],
                    scraper_request=scraper_request,
                    folder_id=folder.id,
                    url=url,
                    user_posted=user_posted,
                    content=content,
                    likes=likes,
                    num_comments=num_comments,
                    shares=shares,
                    date_posted=timezone.now()
                )
                
                posts_created += 1
                
            except Exception as e:
                print(f"⚠️ Error creating post {post_idx}: {e}")
                posts_failed += 1
        
        print(f"📊 Post Results: {posts_created} created, {posts_failed} failed")
        
        result = {
            'snapshot_id': snapshot_info['snapshot_id'],
            'platform': snapshot_info['platform'],
            'folder_id': folder.id,
            'folder_name': folder.name,
            'posts_created': posts_created,
            'api_url': f"/api/brightdata/data-storage/run/{folder.id}/",
            'frontend_url': f"https://trackfutura.futureobjects.io/organizations/1/projects/{project.id}/data-storage"
        }
        
        results.append(result)
    
    print("\n" + "=" * 50)
    print("🎉 SNAPSHOTS SAVED!")
    
    total_posts = sum(r['posts_created'] for r in results)
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['platform'].upper()}: {result['posts_created']} posts")
        print(f"   📁 Folder ID: {result['folder_id']}")
        print(f"   🔗 API: {result['api_url']}")
    
    print(f"\n📈 TOTAL POSTS: {total_posts}")
    
    if results:
        main_url = results[0]['frontend_url']
        print(f"\n🌐 FRONTEND ACCESS:")
        print(f"   {main_url}")
        print(f"   Navigate to 'Data Storage' to see your folders")
        return main_url
    
    return None

if __name__ == "__main__":
    try:
        url = save_snapshots_simple()
        if url:
            print(f"\n✅ SUCCESS! Frontend URL: {url}")
        else:
            print(f"\n❌ No snapshots processed")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()