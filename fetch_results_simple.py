from brightdata_integration.models import BrightDataScrapedPost, BrightDataScraperRequest
from brightdata_integration.services import BrightDataAutomatedBatchScraper

print("🔍 FETCHING PENDING BRIGHTDATA RESULTS")
print("=" * 50)

# Get processing requests
processing_requests = BrightDataScraperRequest.objects.filter(
    status='processing'
).exclude(
    snapshot_id__startswith='emergency_snapshot_'
).exclude(
    snapshot_id__isnull=True
).order_by('-created_at')

print(f"Found {processing_requests.count()} processing requests")

scraper_service = BrightDataAutomatedBatchScraper()

for request in processing_requests[:3]:  # Check first 3
    print(f"\nChecking Request {request.id}:")
    print(f"  Snapshot: {request.snapshot_id}")
    print(f"  Platform: {request.platform}")
    print(f"  Folder: {request.folder_id}")
    
    try:
        results = scraper_service.get_dataset_results(request.snapshot_id)
        
        if results and len(results) > 0:
            print(f"  ✅ Found {len(results)} results!")
            
            # Save results
            saved_count = 0
            for i, result in enumerate(results):
                post, created = BrightDataScrapedPost.objects.get_or_create(
                    post_id=result.get('post_id', f'bd_{request.snapshot_id}_{i}'),
                    defaults={
                        'platform': request.platform,
                        'url': result.get('url', ''),
                        'user_posted': result.get('username', 'unknown'),
                        'content': result.get('content', result.get('caption', 'No content')),
                        'likes': result.get('likes', 0),
                        'num_comments': result.get('comments', 0),
                        'folder_id': request.folder_id,
                        'source_request': request
                    }
                )
                if created:
                    saved_count += 1
            
            # Update status
            request.status = 'completed'
            request.save()
            
            print(f"  💾 Saved {saved_count} posts, updated status")
        else:
            print(f"  ⏳ No results yet")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")

print("\n✅ Fetch operation completed!")