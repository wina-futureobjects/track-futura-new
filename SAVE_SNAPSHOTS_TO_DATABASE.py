#!/usr/bin/env python3
"""
🎯 SAVE BRIGHTDATA SNAPSHOTS TO DATABASE
Save your latest 2 snapshots to database and create frontend data storage
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
    BrightDataBatchJob,
    BrightDataWebhookEvent
)
from track_accounts.models import UnifiedRunFolder
from users.models import Project
from django.utils import timezone

def save_snapshots_to_database():
    """Save the 2 latest snapshots to database and create data storage folders"""
    
    print("🎯 SAVING BRIGHTDATA SNAPSHOTS TO DATABASE")
    print("=" * 60)
    
    # Your latest 2 snapshot files
    snapshot_files = [
        {
            'data_file': 'snapshot_s_mgp6kcyu28lbyl8rx9_data_20251013_214727.json',
            'metadata_file': 'snapshot_s_mgp6kcyu28lbyl8rx9_metadata_20251013_214726.json',
            'snapshot_id': 's_mgp6kcyu28lbyl8rx9',
            'platform': 'facebook',
            'source': 'Nike Facebook'
        },
        {
            'data_file': 'snapshot_s_mgp6kclbi353dgcjk_data_20251013_214729.json',
            'metadata_file': 'snapshot_s_mgp6kclbi353dgcjk_metadata_20251013_214727.json',
            'snapshot_id': 's_mgp6kclbi353dgcjk',
            'platform': 'instagram',
            'source': 'Nike Instagram'
        }
    ]
    
    results = []
    
    for i, snapshot_info in enumerate(snapshot_files, 1):
        print(f"\n📊 PROCESSING SNAPSHOT {i}: {snapshot_info['snapshot_id']}")
        
        # Check if files exist
        data_file = snapshot_info['data_file']
        metadata_file = snapshot_info['metadata_file']
        
        if not os.path.exists(data_file):
            print(f"❌ Data file not found: {data_file}")
            continue
        
        if not os.path.exists(metadata_file):
            print(f"❌ Metadata file not found: {metadata_file}")
            continue
            
        # Load data
        try:
            print(f"📄 Loading data from {data_file}...")
            with open(data_file, 'r', encoding='utf-8') as f:
                data_content = f.read()
                
            # Parse the JSON data - Handle JSONL format (multiple JSON objects on separate lines)
            posts_data = []
            
            if data_content.startswith('['):
                # Array of posts
                posts_data = json.loads(data_content)
            elif data_content.startswith('{'):
                # Could be JSONL format (multiple JSON objects) or single object
                lines = data_content.strip().split('\n')
                
                if len(lines) == 1:
                    # Single JSON object
                    json_data = json.loads(data_content)
                    if 'data' in json_data:
                        posts_data = json_data['data']
                    else:
                        posts_data = [json_data]
                else:
                    # Multiple JSON objects (JSONL format)
                    for line in lines:
                        line = line.strip()
                        if line:
                            try:
                                post_obj = json.loads(line)
                                posts_data.append(post_obj)
                            except json.JSONDecodeError as e:
                                print(f"⚠️ Skipping invalid JSON line: {line[:50]}...")
                                continue
            else:
                print(f"❌ Unexpected data format in {data_file}")
                continue
                
            print(f"✅ Loaded {len(posts_data)} posts from {data_file}")
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            continue
        
        # Load metadata
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            print(f"✅ Loaded metadata from {metadata_file}")
        except Exception as e:
            print(f"⚠️ Error loading metadata: {e}")
            metadata = {}
        
        # Get or create project
        project, created = Project.objects.get_or_create(
            id=1,
            defaults={
                'name': 'TrackFutura Social Media Monitoring',
                'description': 'Main project for social media data collection'
            }
        )
        
        if created:
            print(f"✅ Created project: {project.name}")
        
        # Create folder for this snapshot
        folder_name = f"{snapshot_info['source']} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        folder, folder_created = UnifiedRunFolder.objects.get_or_create(
            name=folder_name,
            defaults={
                'project_id': project.id,
                'folder_type': 'job',
                'platform_code': snapshot_info['platform'],
                'service_code': 'posts',
                'description': f"BrightData snapshot {snapshot_info['snapshot_id']}"
            }
        )
        
        if folder_created:
            print(f"✅ Created folder: {folder.name} (ID: {folder.id})")
        else:
            print(f"♻️ Using existing folder: {folder.name} (ID: {folder.id})")
        
        # Create scraper request
        scraper_request, req_created = BrightDataScraperRequest.objects.get_or_create(
            snapshot_id=snapshot_info['snapshot_id'],
            defaults={
                'platform': snapshot_info['platform'],
                'target_url': f"BrightData snapshot {snapshot_info['snapshot_id']}",
                'source_name': snapshot_info['source'],
                'folder_id': folder.id,
                'status': 'completed',
                'scrape_number': 1,
                'completed_at': timezone.now()
            }
        )
        
        if req_created:
            print(f"✅ Created scraper request: {scraper_request.id}")
        else:
            print(f"♻️ Using existing scraper request: {scraper_request.id}")
            # Update folder_id if different
            if scraper_request.folder_id != folder.id:
                scraper_request.folder_id = folder.id
                scraper_request.save()
                print(f"🔄 Updated scraper request folder_id to {folder.id}")
        
        # Create webhook event
        webhook_event, webhook_created = BrightDataWebhookEvent.objects.get_or_create(
            event_id=f"manual_import_{snapshot_info['snapshot_id']}",
            defaults={
                'snapshot_id': snapshot_info['snapshot_id'],
                'platform': snapshot_info['platform'],
                'status': 'completed',
                'raw_data': posts_data[:5],  # Store first 5 posts as sample
                'processed_at': timezone.now()
            }
        )
        
        if webhook_created:
            print(f"✅ Created webhook event: {webhook_event.event_id}")
        
        # Process each post
        posts_created = 0
        posts_updated = 0
        posts_skipped = 0
        
        print(f"📝 Processing {len(posts_data)} posts...")
        
        for post_data in posts_data:
            try:
                # Extract post information based on platform
                if snapshot_info['platform'] == 'instagram':
                    post_info = {
                        'post_id': post_data.get('post_id') or post_data.get('id', f"ig_{int(datetime.now().timestamp())}"),
                        'url': post_data.get('url', ''),
                        'user_posted': post_data.get('user_posted') or post_data.get('username', ''),
                        'content': post_data.get('description') or post_data.get('content', ''),
                        'likes': post_data.get('likes_count', 0) or post_data.get('likes', 0),
                        'num_comments': post_data.get('comments_count', 0) or post_data.get('num_comments', 0),
                        'media_type': post_data.get('media_type', 'unknown'),
                        'hashtags': post_data.get('hashtags', []),
                        'is_verified': post_data.get('is_verified', False)
                    }
                else:  # Facebook
                    post_info = {
                        'post_id': post_data.get('post_id') or post_data.get('id', f"fb_{int(datetime.now().timestamp())}"),
                        'url': post_data.get('url', ''),
                        'user_posted': post_data.get('user_username_raw') or post_data.get('user_posted', ''),
                        'content': post_data.get('content') or post_data.get('post_text', ''),
                        'likes': post_data.get('likes_count', 0) or post_data.get('likes', 0),
                        'num_comments': post_data.get('comments_count', 0) or post_data.get('num_comments', 0),
                        'shares': post_data.get('shares_count', 0) or post_data.get('shares', 0),
                        'media_type': post_data.get('media_type', 'unknown'),
                        'is_verified': post_data.get('is_verified', False)
                    }
                
                # Create or update the scraped post
                scraped_post, post_created = BrightDataScrapedPost.objects.get_or_create(
                    post_id=post_info['post_id'],
                    platform=snapshot_info['platform'],
                    defaults={
                        'scraper_request': scraper_request,
                        'folder_id': folder.id,
                        'url': post_info['url'],
                        'user_posted': post_info['user_posted'],
                        'content': post_info['content'],
                        'likes': post_info['likes'],
                        'num_comments': post_info['num_comments'],
                        'shares': post_info.get('shares', 0),
                        'media_type': post_info['media_type'],
                        'hashtags': post_info.get('hashtags', []),
                        'is_verified': post_info['is_verified'],
                        'raw_data': post_data,
                        'date_posted': timezone.now()
                    }
                )
                
                if post_created:
                    posts_created += 1
                else:
                    # Update if existing
                    if scraped_post.folder_id != folder.id:
                        scraped_post.folder_id = folder.id
                        scraped_post.scraper_request = scraper_request
                        scraped_post.save()
                        posts_updated += 1
                    else:
                        posts_skipped += 1
                        
            except Exception as e:
                print(f"⚠️ Error processing post: {e}")
                posts_skipped += 1
                continue
        
        print(f"📊 Post Processing Results:")
        print(f"   ✅ Created: {posts_created}")
        print(f"   🔄 Updated: {posts_updated}")
        print(f"   ⚠️ Skipped: {posts_skipped}")
        print(f"   📝 Total: {posts_created + posts_updated + posts_skipped}")
        
        # Create result summary
        result = {
            'snapshot_id': snapshot_info['snapshot_id'],
            'platform': snapshot_info['platform'],
            'source': snapshot_info['source'],
            'folder_id': folder.id,
            'folder_name': folder.name,
            'scraper_request_id': scraper_request.id,
            'posts_created': posts_created,
            'posts_updated': posts_updated,
            'posts_total': posts_created + posts_updated,
            'data_storage_url': f"/organizations/1/projects/{project.id}/data-storage/run/{folder.id}/",
            'api_url': f"/api/brightdata/data-storage/run/{folder.id}/",
            'frontend_url': f"https://trackfutura.futureobjects.io/organizations/1/projects/{project.id}/data-storage"
        }
        
        results.append(result)
        
        print(f"🎉 SNAPSHOT {i} SAVED SUCCESSFULLY!")
        print(f"   📁 Folder ID: {folder.id}")
        print(f"   📝 Posts: {result['posts_total']}")
        print(f"   🌐 API URL: {result['api_url']}")
        print(f"   🖥️ Frontend URL: {result['frontend_url']}")
    
    print("\n" + "=" * 60)
    print("🎉 ALL SNAPSHOTS SAVED TO DATABASE!")
    print("\n📊 SUMMARY:")
    
    total_posts = sum(r['posts_total'] for r in results)
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['source']} ({result['platform'].upper()})")
        print(f"   📋 Snapshot ID: {result['snapshot_id']}")
        print(f"   📁 Folder: {result['folder_name']} (ID: {result['folder_id']})")
        print(f"   📝 Posts: {result['posts_total']}")
        print(f"   🔗 API: {result['api_url']}")
        print(f"   🌐 Frontend: {result['frontend_url']}")
    
    print(f"\n📈 TOTAL POSTS SAVED: {total_posts}")
    
    # Return the main frontend URL
    main_frontend_url = results[0]['frontend_url'] if results else None
    
    print(f"\n🎯 MAIN FRONTEND ACCESS:")
    print(f"   🌐 {main_frontend_url}")
    print(f"   📁 Navigate to 'Data Storage' to see your saved snapshots")
    
    return {
        'success': True,
        'snapshots_processed': len(results),
        'total_posts': total_posts,
        'results': results,
        'frontend_url': main_frontend_url
    }

if __name__ == "__main__":
    try:
        result = save_snapshots_to_database()
        print(f"\n✅ SUCCESS: {result['snapshots_processed']} snapshots saved with {result['total_posts']} posts!")
        print(f"🔗 Frontend URL: {result['frontend_url']}")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()