#!/usr/bin/env python3

import os
import sys
import django

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apify_integration.models import ApifyBatchJob, ApifyScraperRequest
from instagram_data.models import Folder, InstagramPost

def debug_batch_job_8():
    """Debug what's happening with batch job 8"""
    print("🔍 Debugging batch job 8...")
    
    try:
        # Get batch job 8
        batch_job = ApifyBatchJob.objects.get(id=8)
        print(f"✅ Batch job: {batch_job.name}")
        print(f"   Status: {batch_job.status}")
        print(f"   Project: {batch_job.project.name}")
        
        # Check scraper requests
        scraper_requests = batch_job.scraper_requests.all()
        print(f"📊 Scraper requests: {scraper_requests.count()}")
        
        for req in scraper_requests:
            print(f"   - Request ID: {req.id}, Status: {req.status}, Platform: {req.platform}")
        
        # Check Instagram folders for this project
        project = batch_job.project
        folders = Folder.objects.filter(project=project)
        print(f"📁 Instagram folders in project: {folders.count()}")
        
        for folder in folders:
            posts_count = folder.posts.count()
            print(f"   - {folder.name}: {posts_count} posts")
            if posts_count > 0:
                sample_post = folder.posts.first()
                print(f"     Sample post: {sample_post.user_posted} - {sample_post.description[:50]}...")
        
        # Check specifically for Nike folder
        nike_folders = Folder.objects.filter(
            project=project,
            name__icontains="Nike"
        )
        print(f"🏃 Nike folders: {nike_folders.count()}")
        for folder in nike_folders:
            print(f"   - {folder.name}: {folder.posts.count()} posts")
        
        # Check what the _get_platform_results function would find
        print("\n🔍 Checking what _get_platform_results would find...")
        for req in scraper_requests.filter(status='completed'):
            print(f"Processing request {req.id} (platform: {req.platform})")
            
            if req.platform and req.platform.startswith('instagram'):
                # This is the same logic as in _get_platform_results
                search_folders = Folder.objects.filter(
                    project=batch_job.project,
                    name__icontains=f"{batch_job.name} - Instagram"
                )
                print(f"   Looking for folders containing: '{batch_job.name} - Instagram'")
                print(f"   Found {search_folders.count()} matching folders")
                
                for folder in search_folders:
                    print(f"     - {folder.name}: {folder.posts.count()} posts")
        
    except ApifyBatchJob.DoesNotExist:
        print("❌ Batch job 8 not found")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    debug_batch_job_8()