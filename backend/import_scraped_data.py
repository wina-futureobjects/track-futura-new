"""
Import BrightData scraped files using Django shell
Run: python manage.py shell < import_scraped_data.py
"""

import os
import json
from datetime import datetime
from workflow.models import ScrapingRun, ScrapingJob
from brightdata_integration.models import BrightDataScrapedPost
from users.models import Project

print("🚀 Starting BrightData Scraped Files Import...")

# Get or create a project
project, _ = Project.objects.get_or_create(
    id=1,
    defaults={'name': 'BrightData Import Project', 'description': 'Import scraped data'}
)

# Create scraping runs for Instagram and Facebook
instagram_run, _ = ScrapingRun.objects.get_or_create(
    id=400,
    defaults={
        'project': project,
        'name': 'Instagram Scraped Data Import',
        'status': 'completed',
        'configuration': {'platform': 'instagram', 'imported_from': 'brightdata_files'}
    }
)

facebook_run, _ = ScrapingRun.objects.get_or_create(
    id=401,
    defaults={
        'project': project,
        'name': 'Facebook Scraped Data Import',
        'status': 'completed',
        'configuration': {'platform': 'facebook', 'imported_from': 'brightdata_files'}
    }
)

# Import Instagram data
instagram_file = r"C:\Users\winam\Downloads\bd_20251013_024949_0.json"
if os.path.exists(instagram_file):
    print("📱 Processing Instagram data...")
    with open(instagram_file, 'r', encoding='utf-8') as f:
        instagram_posts = json.load(f)
    
    # Create a job for Instagram
    instagram_job, _ = ScrapingJob.objects.get_or_create(
        scraping_run=instagram_run,
        job_id='instagram_import_001',
        defaults={
            'status': 'completed',
            'result_data': {'total_posts': len(instagram_posts), 'platform': 'instagram'}
        }
    )
    
    # Import posts
    count = 0
    for post_data in instagram_posts:
        try:
            post, created = BrightDataScrapedPost.objects.get_or_create(
                post_id=post_data.get('post_id', post_data.get('shortcode', f'ig_{count}')),
                platform='instagram',
                folder_id=400,  # Using run ID as folder ID
                defaults={
                    'user_posted': post_data.get('user_posted', 'unknown'),
                    'content': post_data.get('description', ''),
                    'description': post_data.get('description', ''),
                    'likes': post_data.get('likes', 0),
                    'num_comments': post_data.get('num_comments', 0),
                    'date_posted': datetime.fromisoformat(post_data.get('timestamp', '2025-10-13T02:50:00.000Z').replace('Z', '+00:00')),
                    'url': post_data.get('url', ''),
                    'raw_data': post_data
                }
            )
            if created:
                count += 1
                print(f"✅ IG {count}: {post_data.get('user_posted', 'unknown')} - {post_data.get('description', '')[:30]}...")
        except Exception as e:
            print(f"❌ Instagram error: {e}")
    
    instagram_run.successful_jobs = 1
    instagram_run.total_jobs = 1
    instagram_run.completed_jobs = 1
    instagram_run.save()
    
    print(f"📱 Instagram: {count} posts imported")

# Import Facebook data
facebook_file = r"C:\Users\winam\Downloads\bd_20251013_024949_0 (1).json"
if os.path.exists(facebook_file):
    print("📘 Processing Facebook data...")
    with open(facebook_file, 'r', encoding='utf-8') as f:
        facebook_posts = json.load(f)
    
    # Create a job for Facebook
    facebook_job, _ = ScrapingJob.objects.get_or_create(
        scraping_run=facebook_run,
        job_id='facebook_import_001',
        defaults={
            'status': 'completed',
            'result_data': {'total_posts': len(facebook_posts), 'platform': 'facebook'}
        }
    )
    
    # Import posts
    count = 0
    for post_data in facebook_posts:
        try:
            post, created = BrightDataScrapedPost.objects.get_or_create(
                post_id=post_data.get('post_id', post_data.get('shortcode', f'fb_{count}')),
                platform='facebook',
                folder_id=401,  # Using run ID as folder ID
                defaults={
                    'user_posted': post_data.get('user_username_raw', 'unknown'),
                    'content': post_data.get('content', ''),
                    'description': post_data.get('content', ''),
                    'likes': post_data.get('likes', post_data.get('num_likes_type', {}).get('num', 0)),
                    'num_comments': post_data.get('num_comments', 0),
                    'date_posted': datetime.fromisoformat(post_data.get('date_posted', '2025-10-13T02:50:00.000Z').replace('Z', '+00:00')),
                    'url': post_data.get('url', ''),
                    'raw_data': post_data
                }
            )
            if created:
                count += 1
                print(f"✅ FB {count}: {post_data.get('user_username_raw', 'unknown')} - {post_data.get('content', '')[:30]}...")
        except Exception as e:
            print(f"❌ Facebook error: {e}")
    
    facebook_run.successful_jobs = 1
    facebook_run.total_jobs = 1
    facebook_run.completed_jobs = 1
    facebook_run.save()
    
    print(f"📘 Facebook: {count} posts imported")

print("\n🎉 Import Complete!")
print(f"📊 Instagram API: http://localhost:8000/api/run-info/400/")
print(f"📊 Facebook API: http://localhost:8000/api/run-info/401/")
print(f"🌐 Frontend (Instagram): https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/run/400")  
print(f"🌐 Frontend (Facebook): https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/run/401")