#!/usr/bin/env python3
"""
Direct Data Import Script for BrightData Files
==============================================
"""
import os
import sys
import json
from datetime import datetime

# Add Django to path and setup
sys.path.append('/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trackfutura.settings')

import django
django.setup()

from core.models import Job, DataStorage, Post

def import_data():
    print("🚀 BRIGHTDATA SCRAPED FILES IMPORT")
    print("=" * 50)
    
    # File paths
    instagram_file = r"C:\Users\winam\Downloads\bd_20251013_024949_0.json"
    facebook_file = r"C:\Users\winam\Downloads\bd_20251013_024949_0 (1).json"
    
    total_imported = 0
    
    # Import Instagram data
    if os.path.exists(instagram_file):
        with open(instagram_file, 'r', encoding='utf-8') as f:
            instagram_posts = json.load(f)
        
        # Create job for Instagram
        job, _ = Job.objects.get_or_create(
            id=5,
            defaults={
                'name': f'Instagram BrightData Import - {datetime.now().strftime("%Y-%m-%d %H:%M")}',
                'description': 'Imported from scraped Instagram posts JSON file',
                'status': 'completed'
            }
        )
        
        # Create DataStorage for Instagram
        data_storage, _ = DataStorage.objects.get_or_create(
            job=job,
            run_id=400,
            defaults={
                'data_type': 'instagram_scraped',
                'file_path': f'/brightdata/instagram_{datetime.now().strftime("%Y%m%d")}.json',
                'total_posts': len(instagram_posts),
                'status': 'completed'
            }
        )
        
        # Import Instagram posts
        instagram_count = 0
        for post_data in instagram_posts:
            try:
                post, created = Post.objects.get_or_create(
                    data_storage=data_storage,
                    post_id=post_data.get('post_id', post_data.get('shortcode', f'ig_{instagram_count}')),
                    defaults={
                        'platform': 'instagram',
                        'user_posted': post_data.get('user_posted', 'unknown'),
                        'description': post_data.get('description', ''),
                        'date_posted': datetime.fromisoformat(post_data.get('timestamp', '2025-10-13T02:50:00.000Z').replace('Z', '+00:00')),
                        'likes': post_data.get('likes', 0),
                        'num_comments': post_data.get('num_comments', 0),
                        'profile_url': post_data.get('profile_url', ''),
                        'post_url': post_data.get('url', ''),
                        'raw_data': json.dumps(post_data)
                    }
                )
                if created:
                    instagram_count += 1
                    print(f"✅ IG: {post_data.get('user_posted', 'unknown')} - {post_data.get('description', '')[:30]}...")
            except Exception as e:
                print(f"❌ IG Error: {e}")
        
        data_storage.total_posts = instagram_count
        data_storage.save()
        total_imported += instagram_count
        print(f"📱 Instagram Complete: {instagram_count} posts imported")
        
    # Import Facebook data  
    if os.path.exists(facebook_file):
        with open(facebook_file, 'r', encoding='utf-8') as f:
            facebook_posts = json.load(f)
        
        # Create job for Facebook
        job, _ = Job.objects.get_or_create(
            id=6,
            defaults={
                'name': f'Facebook BrightData Import - {datetime.now().strftime("%Y-%m-%d %H:%M")}',
                'description': 'Imported from scraped Facebook posts JSON file',
                'status': 'completed'
            }
        )
        
        # Create DataStorage for Facebook
        data_storage, _ = DataStorage.objects.get_or_create(
            job=job,
            run_id=401,
            defaults={
                'data_type': 'facebook_scraped',
                'file_path': f'/brightdata/facebook_{datetime.now().strftime("%Y%m%d")}.json',
                'total_posts': len(facebook_posts),
                'status': 'completed'
            }
        )
        
        # Import Facebook posts
        facebook_count = 0
        for post_data in facebook_posts:
            try:
                post, created = Post.objects.get_or_create(
                    data_storage=data_storage,
                    post_id=post_data.get('post_id', post_data.get('shortcode', f'fb_{facebook_count}')),
                    defaults={
                        'platform': 'facebook',
                        'user_posted': post_data.get('user_username_raw', 'unknown'),
                        'description': post_data.get('content', ''),
                        'date_posted': datetime.fromisoformat(post_data.get('date_posted', '2025-10-13T02:50:00.000Z').replace('Z', '+00:00')),
                        'likes': post_data.get('likes', post_data.get('num_likes_type', {}).get('num', 0)),
                        'num_comments': post_data.get('num_comments', 0),
                        'profile_url': post_data.get('user_url', ''),
                        'post_url': post_data.get('url', ''),
                        'raw_data': json.dumps(post_data)
                    }
                )
                if created:
                    facebook_count += 1
                    print(f"✅ FB: {post_data.get('user_username_raw', 'unknown')} - {post_data.get('content', '')[:30]}...")
            except Exception as e:
                print(f"❌ FB Error: {e}")
        
        data_storage.total_posts = facebook_count
        data_storage.save()
        total_imported += facebook_count
        print(f"📘 Facebook Complete: {facebook_count} posts imported")
    
    print("\n" + "=" * 50)
    print(f"🎉 IMPORT COMPLETE: {total_imported} total posts imported")
    print(f"📊 Instagram API: http://localhost:8000/api/run-info/400/")
    print(f"📊 Facebook API: http://localhost:8000/api/run-info/401/") 
    print(f"🌐 Frontend (Instagram): https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/run/400")
    print(f"🌐 Frontend (Facebook): https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/run/401")

if __name__ == "__main__":
    import_data()