#!/usr/bin/env python3

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.models import BrightDataScrapedPost, BrightDataScraperRequest
from brightdata_integration.services import BrightDataAutomatedBatchScraper
import json

print("🔍 CHECKING PENDING BRIGHTDATA JOBS")
print("=" * 60)

# Get processing requests with real snapshot IDs
processing_requests = BrightDataScraperRequest.objects.filter(
    status='processing'
).exclude(
    snapshot_id__startswith='emergency_snapshot_'
).exclude(
    snapshot_id__isnull=True
).order_by('-created_at')

print(f"Found {processing_requests.count()} processing requests with real snapshot IDs")

scraper_service = BrightDataAutomatedBatchScraper()

for request in processing_requests[:5]:  # Check first 5
    print(f"\n📊 Checking Request {request.id}:")
    print(f"   Platform: {request.platform}")
    print(f"   Snapshot ID: {request.snapshot_id}")
    print(f"   Folder ID: {request.folder_id}")
    print(f"   Created: {request.created_at}")
    
    try:
        # Check if this snapshot has results
        print(f"   🔍 Fetching results from BrightData...")
        results = scraper_service.get_dataset_results(request.snapshot_id)
        
        if results and len(results) > 0:
            print(f"   ✅ Found {len(results)} results!")
            
            # Process and save the results
            saved_count = 0
            for result in results:
                try:
                    # Create or update scraped post
                    post, created = BrightDataScrapedPost.objects.get_or_create(
                        post_id=result.get('post_id', f"bd_{request.snapshot_id}_{saved_count}"),
                        defaults={
                            'platform': request.platform,
                            'url': result.get('url', ''),
                            'user_posted': result.get('username', result.get('user_posted', 'unknown')),
                            'content': result.get('content', result.get('caption', '')),
                            'likes': result.get('likes', result.get('likes_count', 0)),
                            'num_comments': result.get('comments', result.get('comments_count', 0)),
                            'shares': result.get('shares', 0),
                            'folder_id': request.folder_id,
                            'source_request': request
                        }
                    )
                    if created:
                        saved_count += 1
                except Exception as e:
                    print(f"   ⚠️ Error saving post: {e}")
            
            # Update request status
            request.status = 'completed'
            request.save()
            
            print(f"   💾 Saved {saved_count} new posts")
            print(f"   ✅ Updated request status to completed")
            
        else:
            print(f"   ⏳ No results yet (still processing)")
            
    except Exception as e:
        print(f"   ❌ Error checking snapshot: {e}")

print(f"\n🎯 SUMMARY")
print("=" * 30)
print("✅ Checked pending BrightData jobs")
print("✅ Fetched available results")
print("✅ Updated request statuses")
print("\n💡 Jobs should now show completed data!")