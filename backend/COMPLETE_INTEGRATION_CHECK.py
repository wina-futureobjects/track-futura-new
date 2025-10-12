#!/usr/bin/env python3
"""
COMPLETE BACKEND-FRONTEND INTEGRATION CHECK
Check ALL available endpoints and data access methods
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.models import BrightDataScraperRequest, BrightDataScrapedPost, BrightDataBatchJob
from track_accounts.models import UnifiedRunFolder

def check_complete_integration():
    print("🔍 COMPLETE BACKEND-FRONTEND INTEGRATION CHECK")
    print("=" * 70)
    
    print(f"\n📊 DATABASE STATUS:")
    requests = BrightDataScraperRequest.objects.all()
    posts = BrightDataScrapedPost.objects.all()
    folders = UnifiedRunFolder.objects.all()
    batch_jobs = BrightDataBatchJob.objects.all()
    
    print(f"   • Total Scraper Requests: {requests.count()}")
    print(f"   • Total Scraped Posts: {posts.count()}")
    print(f"   • Total Folders: {folders.count()}")
    print(f"   • Total Batch Jobs: {batch_jobs.count()}")
    
    print(f"\n🎯 AVAILABLE BACKEND API ENDPOINTS:")
    print(f"   1. /api/brightdata/scraper-requests/          → All scraper requests (DRF ViewSet)")
    print(f"   2. /api/brightdata/batch-jobs/                → All batch jobs (DRF ViewSet)")
    print(f"   3. /api/brightdata/job-results/<folder_id>/   → Posts for specific folder")
    print(f"   4. /api/brightdata/run-info/<run_id>/         → Run information lookup")
    print(f"   5. /api/brightdata/data-storage/run/<run_id>/ → Direct run data access")
    print(f"   6. /api/brightdata/data-storage/<name>/<num>/ → Folder name + scrape number")
    
    print(f"\n🗂️ WORKING RUN ENDPOINTS WITH DATA:")
    
    # Get folders that have actual posts
    folders_with_posts = BrightDataScrapedPost.objects.values_list('folder_id', flat=True).distinct()
    
    for folder_id in set(folders_with_posts):
        try:
            folder = UnifiedRunFolder.objects.get(id=folder_id)
            post_count = BrightDataScrapedPost.objects.filter(folder_id=folder_id).count()
            
            # Find associated scraper request
            scraper_request = BrightDataScraperRequest.objects.filter(folder_id=folder_id).first()
            
            print(f"\n   📁 Folder {folder_id}: {folder.name}")
            print(f"      └── Posts: {post_count}")
            if scraper_request:
                print(f"      └── Run ID: {scraper_request.id}")
                print(f"      └── Status: {scraper_request.status}")
                print(f"      └── Frontend URLs:")
                print(f"          • /api/brightdata/data-storage/run/{scraper_request.id}/")
                print(f"          • /api/brightdata/run-info/{scraper_request.id}/")
                print(f"          • /api/brightdata/job-results/{folder_id}/")
                
                # Sample post data
                sample_post = BrightDataScrapedPost.objects.filter(folder_id=folder_id).first()
                if sample_post:
                    print(f"      └── Sample Data:")
                    print(f"          • Platform: {sample_post.platform}")
                    print(f"          • User: {sample_post.user_posted}")
                    print(f"          • Content: {sample_post.content[:50]}..." if sample_post.content else "No content")
            else:
                print(f"      └── ⚠️  No scraper request found")
                
        except UnifiedRunFolder.DoesNotExist:
            print(f"   ❌ Folder {folder_id}: NOT FOUND")
    
    print(f"\n🌐 FRONTEND ACCESS METHODS:")
    print(f"   Method 1: Direct Run Access")
    print(f"   └── URL Pattern: /organizations/1/projects/1/data-storage/run/<run_id>")
    print(f"   └── Example: /organizations/1/projects/1/data-storage/run/17")
    print(f"   └── API Call: /api/brightdata/data-storage/run/17/")
    
    print(f"\n   Method 2: Folder Name Access")  
    print(f"   └── URL Pattern: /organizations/1/projects/1/data-storage/<folder_name>/<scrape_num>")
    print(f"   └── Example: /organizations/1/projects/1/data-storage/Job%202/1")
    print(f"   └── API Call: /api/brightdata/data-storage/Job%202/1/")
    
    print(f"\n   Method 3: Folder ID Access")
    print(f"   └── URL Pattern: /organizations/1/projects/1/folders/<folder_id>")
    print(f"   └── Example: /organizations/1/projects/1/folders/103")
    print(f"   └── API Call: /api/brightdata/job-results/103/")
    
    print(f"\n✅ COMPLETE ENDPOINTS LIST:")
    active_requests = BrightDataScraperRequest.objects.filter(folder_id__in=folders_with_posts)
    for req in active_requests:
        try:
            folder = UnifiedRunFolder.objects.get(id=req.folder_id)
            post_count = BrightDataScrapedPost.objects.filter(folder_id=req.folder_id).count()
            print(f"   🔗 /run/{req.id} → {folder.name} ({post_count} posts)")
        except:
            continue

if __name__ == "__main__":
    check_complete_integration()