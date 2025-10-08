"""
BrightData Data Collection Task

This script automatically fetches and saves BrightData results
for completed jobs that haven't been saved to the database yet.
"""

import os
import sys
import django

# Setup Django
sys.path.append('/app/backend')  # Production path
sys.path.append('C:/Users/winam/OneDrive/문서/PREVIOUS/TrackFutura - Copy/backend')  # Local path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.models import BrightDataScraperRequest, BrightDataScrapedPost
from brightdata_integration.services import BrightDataAutomatedBatchScraper
from django.utils import timezone
from datetime import timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def collect_brightdata_results():
    """
    Check for completed BrightData jobs and save their results to database
    """
    print("🔍 Checking for BrightData results to collect...")
    
    # Find scraper requests that are processing but don't have saved posts yet
    pending_requests = BrightDataScraperRequest.objects.filter(
        status='processing',
        snapshot_id__isnull=False
    ).exclude(snapshot_id='')
    
    # Also check requests from the last 24 hours that might be completed
    recent_requests = BrightDataScraperRequest.objects.filter(
        created_at__gte=timezone.now() - timedelta(hours=24),
        snapshot_id__isnull=False
    ).exclude(snapshot_id='')
    
    all_request_ids = set(list(pending_requests.values_list('id', flat=True)) + 
                         list(recent_requests.values_list('id', flat=True)))
    
    all_requests = BrightDataScraperRequest.objects.filter(id__in=all_request_ids)
    
    print(f"📋 Found {all_requests.count()} scraper requests to check")
    
    scraper = BrightDataAutomatedBatchScraper()
    collected_count = 0
    
    for request in all_requests:
        try:
            # Check if we already have posts for this request
            existing_posts = BrightDataScrapedPost.objects.filter(scraper_request=request).count()
            
            if existing_posts > 0:
                print(f"✅ Request {request.id} already has {existing_posts} saved posts")
                continue
            
            print(f"🔄 Checking request {request.id} (snapshot: {request.snapshot_id})")
            
            # Try to fetch and save results
            result = scraper.fetch_and_save_brightdata_results(request.snapshot_id, request)
            
            if result['success']:
                saved_count = result.get('saved_count', 0)
                if saved_count > 0:
                    print(f"✅ Saved {saved_count} posts for request {request.id}")
                    collected_count += saved_count
                else:
                    print(f"📝 No new posts to save for request {request.id}")
            else:
                print(f"❌ Failed to collect results for request {request.id}: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Error processing request {request.id}: {str(e)}")
            continue
    
    print(f"🎉 Collection complete! Saved {collected_count} total posts")
    return collected_count

if __name__ == "__main__":
    try:
        collected = collect_brightdata_results()
        print(f"\n📊 SUMMARY: Collected {collected} posts from BrightData")
    except Exception as e:
        print(f"❌ Collection failed: {str(e)}")
        sys.exit(1)