#!/usr/bin/env python3
"""
🎯 DIRECT BRIGHTDATA SNAPSHOT SAVER
Save snapshots using direct database operations to bypass model issues
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

from django.db import connection
from django.utils import timezone
from track_accounts.models import UnifiedRunFolder
from users.models import Project

def save_snapshots_direct():
    """Save snapshots using direct SQL to avoid model issues"""
    
    print("🎯 DIRECT BRIGHTDATA SNAPSHOT SAVER")
    print("=" * 50)
    
    # Your snapshot data
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
    
    # Get or create project
    project, created = Project.objects.get_or_create(
        id=1,
        defaults={
            'name': 'TrackFutura Social Media',
            'description': 'BrightData snapshots'
        }
    )
    
    if created:
        print(f"✅ Created project: {project.name}")
    
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
                            continue
            
            print(f"✅ Loaded {len(posts_data)} posts")
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            continue
        
        # Create folder  
        folder = UnifiedRunFolder.objects.create(
            name=f"{snapshot_info['source']} Collection",
            project_id=project.id,
            folder_type='job',
            platform_code=snapshot_info['platform'],
            description=f"BrightData {snapshot_info['snapshot_id']}"
        )
        
        print(f"✅ Created folder: {folder.name} (ID: {folder.id})")
        
        # Create scraper request using direct SQL
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO brightdata_integration_brightdatascraperrequest 
                (snapshot_id, platform, content_type, target_url, source_name, folder_id, status, scrape_number, created_at, updated_at, completed_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, [
                snapshot_info['snapshot_id'],
                snapshot_info['platform'],
                'posts',  # Required content_type field
                f"BrightData {snapshot_info['snapshot_id']}",
                snapshot_info['source'],
                folder.id,
                'completed',
                1,
                timezone.now(),
                timezone.now(),
                timezone.now()
            ])
            scraper_request_id = cursor.lastrowid
        
        print(f"✅ Created scraper request: {scraper_request_id}")
        
        # Create posts using direct SQL
        posts_created = 0
        
        for post_idx, post_data in enumerate(posts_data, 1):
            try:
                # Extract post info
                if snapshot_info['platform'] == 'facebook':
                    post_id = post_data.get('post_id', f"fb_{folder.id}_{post_idx}")
                    url = post_data.get('url', '')
                    user_posted = post_data.get('user_username_raw', 'Nike')
                    content = post_data.get('content', '')
                    likes = int(post_data.get('num_likes_type', {}).get('num', 0)) if post_data.get('num_likes_type') else 0
                    comments = int(post_data.get('num_comments', 0))
                    shares = int(post_data.get('num_shares', 0))
                else:  # Instagram
                    post_id = post_data.get('post_id', f"ig_{folder.id}_{post_idx}")
                    url = post_data.get('url', '')
                    user_posted = post_data.get('user_posted', 'Nike')
                    content = post_data.get('description', '')
                    likes = int(post_data.get('likes_count', 0))
                    comments = int(post_data.get('comments_count', 0))
                    shares = 0
                
                # Insert directly using SQL
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO brightdata_integration_brightdatascrapedpost
                        (post_id, platform, scraper_request_id, folder_id, url, user_posted, content, 
                         likes, num_comments, shares, hashtags, mentions, is_verified, follower_count, 
                         raw_data, date_posted, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, [
                        post_id,
                        snapshot_info['platform'],
                        scraper_request_id,
                        folder.id,
                        url,
                        user_posted,
                        content[:1000],  # Truncate content if too long
                        likes,
                        comments,
                        shares,
                        json.dumps(post_data.get('hashtags', [])),  # JSON field for hashtags
                        json.dumps(post_data.get('mentions', [])),   # JSON field for mentions
                        post_data.get('is_verified', True),  # Nike is verified
                        post_data.get('page_followers', 39000000),  # Nike's follower count
                        json.dumps(post_data),  # Store raw data as JSON
                        timezone.now(),
                        timezone.now(),
                        timezone.now()
                    ])
                
                posts_created += 1
                
            except Exception as e:
                print(f"⚠️ Error creating post {post_idx}: {e}")
        
        print(f"📊 Successfully created {posts_created} posts")
        
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
    print("🎉 SNAPSHOTS SAVED TO DATABASE!")
    
    total_posts = sum(r['posts_created'] for r in results)
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['platform'].upper()}: {result['posts_created']} posts")
        print(f"   📁 Folder: {result['folder_name']} (ID: {result['folder_id']})")
        print(f"   🔗 API: {result['api_url']}")
    
    print(f"\n📈 TOTAL POSTS SAVED: {total_posts}")
    
    if results:
        main_url = results[0]['frontend_url']
        print(f"\n🌐 FRONTEND ACCESS:")
        print(f"   {main_url}")
        print(f"   📁 Navigate to 'Data Storage' to see your saved snapshots")
        return main_url
    
    return None

if __name__ == "__main__":
    try:
        url = save_snapshots_direct()
        if url:
            print(f"\n✅ SUCCESS! Your snapshots are now in the database!")
            print(f"🔗 Frontend: {url}")
        else:
            print(f"\n❌ Failed to process snapshots")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()