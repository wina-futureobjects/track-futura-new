#!/usr/bin/env python3
"""
BrightData Scraped Files Import Script
====================================
This script imports the scraped Instagram and Facebook data files 
from the Downloads folder into the TrackFutura data storage system.

Usage: python import_brightdata_files.py
"""

import os
import sys
import json
import django
from datetime import datetime
from pathlib import Path

# Add the backend directory to Python path  
backend_dir = Path(__file__).parent / 'backend'
sys.path.append(str(backend_dir))
os.chdir(str(backend_dir))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trackfutura.settings')
django.setup()

from core.models import Job, DataStorage, Post

def import_instagram_data(file_path):
    """Import Instagram posts from JSON file"""
    print(f"📱 Importing Instagram data from: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        instagram_posts = json.load(f)
    
    # Create or get job for Instagram import
    job, created = Job.objects.get_or_create(
        id=5,  # New job ID for scraped data
        defaults={
            'name': f'Instagram Scraped Data Import - {datetime.now().strftime("%Y-%m-%d %H:%M")}',
            'description': 'Imported from BrightData scraped files',
            'status': 'completed',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
    )
    
    # Create DataStorage entry for Instagram
    data_storage, created = DataStorage.objects.get_or_create(
        job=job,
        run_id=400,  # New run ID for scraped data
        defaults={
            'data_type': 'instagram',
            'file_path': f'/data/instagram_scraped_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            'total_posts': len(instagram_posts),
            'status': 'completed',
            'created_at': datetime.now()
        }
    )
    
    imported_count = 0
    for post_data in instagram_posts:
        try:
            # Create Post entry
            post, created = Post.objects.get_or_create(
                data_storage=data_storage,
                post_id=post_data.get('post_id', post_data.get('shortcode', f'unknown_{imported_count}')),
                defaults={
                    'platform': 'instagram',
                    'user_posted': post_data.get('user_posted', 'unknown'),
                    'description': post_data.get('description', ''),
                    'date_posted': datetime.fromisoformat(post_data.get('timestamp', '2025-10-13T00:00:00.000Z').replace('Z', '+00:00')),
                    'likes': post_data.get('likes', 0),
                    'num_comments': post_data.get('num_comments', 0),
                    'profile_url': post_data.get('profile_url', ''),
                    'post_url': post_data.get('url', ''),
                    'raw_data': json.dumps(post_data)
                }
            )
            if created:
                imported_count += 1
                print(f"✅ Imported Instagram post: {post_data.get('user_posted', 'unknown')} - {post_data.get('description', '')[:50]}...")
        except Exception as e:
            print(f"❌ Error importing Instagram post: {e}")
    
    print(f"📊 Instagram Import Complete: {imported_count} posts imported")
    return data_storage, imported_count

def import_facebook_data(file_path):
    """Import Facebook posts from JSON file"""
    print(f"📘 Importing Facebook data from: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        facebook_posts = json.load(f)
    
    # Create or get job for Facebook import
    job, created = Job.objects.get_or_create(
        id=6,  # New job ID for Facebook scraped data
        defaults={
            'name': f'Facebook Scraped Data Import - {datetime.now().strftime("%Y-%m-%d %H:%M")}',
            'description': 'Imported from BrightData scraped files',
            'status': 'completed',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
    )
    
    # Create DataStorage entry for Facebook
    data_storage, created = DataStorage.objects.get_or_create(
        job=job,
        run_id=401,  # New run ID for Facebook scraped data
        defaults={
            'data_type': 'facebook',
            'file_path': f'/data/facebook_scraped_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            'total_posts': len(facebook_posts),
            'status': 'completed',
            'created_at': datetime.now()
        }
    )
    
    imported_count = 0
    for post_data in facebook_posts:
        try:
            # Create Post entry
            post, created = Post.objects.get_or_create(
                data_storage=data_storage,
                post_id=post_data.get('post_id', post_data.get('shortcode', f'facebook_unknown_{imported_count}')),
                defaults={
                    'platform': 'facebook',
                    'user_posted': post_data.get('user_username_raw', 'unknown'),
                    'description': post_data.get('content', ''),
                    'date_posted': datetime.fromisoformat(post_data.get('date_posted', '2025-10-13T00:00:00.000Z').replace('Z', '+00:00')),
                    'likes': post_data.get('likes', post_data.get('num_likes_type', {}).get('num', 0)),
                    'num_comments': post_data.get('num_comments', 0),
                    'profile_url': post_data.get('user_url', ''),
                    'post_url': post_data.get('url', ''),
                    'raw_data': json.dumps(post_data)
                }
            )
            if created:
                imported_count += 1
                print(f"✅ Imported Facebook post: {post_data.get('user_username_raw', 'unknown')} - {post_data.get('content', '')[:50]}...")
        except Exception as e:
            print(f"❌ Error importing Facebook post: {e}")
    
    print(f"📊 Facebook Import Complete: {imported_count} posts imported")
    return data_storage, imported_count

def main():
    """Main import function"""
    print("🚀 BRIGHTDATA SCRAPED FILES IMPORT")
    print("=" * 50)
    
    # File paths
    instagram_file = r"C:\Users\winam\Downloads\bd_20251013_024949_0.json"
    facebook_file = r"C:\Users\winam\Downloads\bd_20251013_024949_0 (1).json"
    
    total_imported = 0
    
    # Import Instagram data
    if os.path.exists(instagram_file):
        instagram_storage, instagram_count = import_instagram_data(instagram_file)
        total_imported += instagram_count
        print(f"📱 Instagram DataStorage ID: {instagram_storage.id}, Run ID: {instagram_storage.run_id}")
    else:
        print(f"❌ Instagram file not found: {instagram_file}")
    
    # Import Facebook data  
    if os.path.exists(facebook_file):
        facebook_storage, facebook_count = import_facebook_data(facebook_file)
        total_imported += facebook_count
        print(f"📘 Facebook DataStorage ID: {facebook_storage.id}, Run ID: {facebook_storage.run_id}")
    else:
        print(f"❌ Facebook file not found: {facebook_file}")
    
    print("\n" + "=" * 50)
    print(f"🎉 IMPORT COMPLETE: {total_imported} total posts imported")
    print(f"📊 View data at: http://localhost:8000/api/run-info/400/ (Instagram)")
    print(f"📊 View data at: http://localhost:8000/api/run-info/401/ (Facebook)")
    print(f"🌐 Frontend URL: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/run/400")
    print(f"🌐 Frontend URL: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/run/401")

if __name__ == "__main__":
    main()