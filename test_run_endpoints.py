#!/usr/bin/env python3
"""
Test script to verify /run/ endpoint database connectivity
"""

import os
import sys
import django

# Add the backend directory to the Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.append(backend_path)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.models import BrightDataScraperRequest, BrightDataScrapedPost
from track_accounts.models import UnifiedRunFolder

def test_run_endpoints():
    print("=== Testing /run/ endpoint database connectivity ===\n")
    
    # Get all requests that have scraped data
    folders_with_data = BrightDataScrapedPost.objects.values_list('folder_id', flat=True).distinct()
    print(f"Folders with scraped data: {list(set(folders_with_data))}")
    
    # Get requests for folders that have data
    requests_with_data = BrightDataScraperRequest.objects.filter(
        folder_id__in=folders_with_data
    ).order_by('id')
    
    print(f"\n=== Available /run/ endpoints with data ===")
    for request in requests_with_data:
        try:
            folder = UnifiedRunFolder.objects.get(id=request.folder_id)
            post_count = BrightDataScrapedPost.objects.filter(folder_id=request.folder_id).count()
            
            print(f"/run/{request.id} -> Folder {request.folder_id} ({folder.name})")
            print(f"  Status: {request.status}")
            print(f"  Scrape Number: {request.scrape_number}")
            print(f"  Posts Available: {post_count}")
            print(f"  Sample URL: http://localhost:8000/api/run-info/{request.id}/")
            print()
            
        except UnifiedRunFolder.DoesNotExist:
            print(f"/run/{request.id} -> Folder {request.folder_id} (FOLDER NOT FOUND)")
            continue
    
    print("=== Testing specific run lookups ===")
    
    # Test run 17 and 18 specifically
    for run_id in [17, 18]:
        try:
            request = BrightDataScraperRequest.objects.get(id=run_id)
            folder = UnifiedRunFolder.objects.get(id=request.folder_id)
            posts = BrightDataScrapedPost.objects.filter(folder_id=request.folder_id)
            
            print(f"\n/run/{run_id} DETAILS:")
            print(f"  -> Maps to Folder {request.folder_id} ({folder.name})")
            print(f"  -> Status: {request.status}")
            print(f"  -> Total Posts: {posts.count()}")
            
            if posts.exists():
                sample_post = posts.first()
                print(f"  -> Sample Post: {sample_post.content[:100]}..." if sample_post.content else "No content")
                print(f"  -> Platform: {sample_post.platform}")
                print(f"  -> Date Posted: {sample_post.date_posted}")
            
            print(f"  ✅ /run/{run_id} is CONNECTED to database with {posts.count()} posts")
            
        except BrightDataScraperRequest.DoesNotExist:
            print(f"❌ /run/{run_id} - Request not found")
        except UnifiedRunFolder.DoesNotExist:
            print(f"❌ /run/{run_id} - Folder not found")
        except Exception as e:
            print(f"❌ /run/{run_id} - Error: {e}")

if __name__ == "__main__":
    test_run_endpoints()