from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from brightdata_integration.models import BrightDataScrapedPost, BrightDataScraperRequest
from track_accounts.models import UnifiedRunFolder
import json

@csrf_exempt
@require_http_methods(["GET"])
def simple_brightdata_folders(request):
    """
    SIMPLE ENDPOINT: Show all BrightData scraped jobs in one place
    This will be called directly by the data storage page
    """
    try:
        # Get all BrightData scraper requests that have data
        scraped_jobs = []
        
        # Find all folders that have BrightData scraped posts
        folders_with_data = BrightDataScrapedPost.objects.values_list('folder_id', flat=True).distinct()
        
        for folder_id in folders_with_data:
            if folder_id:
                # Get the folder info
                try:
                    folder = UnifiedRunFolder.objects.get(id=folder_id)
                    post_count = BrightDataScrapedPost.objects.filter(folder_id=folder_id).count()
                    
                    # Get scraper request info if available
                    scraper_request = BrightDataScraperRequest.objects.filter(folder_id=folder_id).first()
                    snapshot_id = scraper_request.snapshot_id if scraper_request else 'Unknown'
                    platform = scraper_request.platform if scraper_request else 'Unknown'
                    
                    scraped_jobs.append({
                        'id': folder.id,
                        'name': f'BrightData Job - {snapshot_id}',
                        'description': f'{platform.title()} scraped data from BrightData ({post_count} posts)',
                        'folder_type': 'job',
                        'category': 'posts',
                        'category_display': 'Posts',
                        'platform': platform,
                        'platform_code': platform,
                        'post_count': post_count,
                        'created_at': folder.created_at.isoformat() if folder.created_at else None,
                        'snapshot_id': snapshot_id,
                        'data_url': f'/organizations/1/projects/2/data-storage/job/{folder.id}',
                        'api_url': f'/api/brightdata/job-results/{folder.id}/',
                        'status': 'completed'
                    })
                except UnifiedRunFolder.DoesNotExist:
                    continue
        
        return JsonResponse({
            'success': True,
            'message': f'Found {len(scraped_jobs)} BrightData scraped jobs',
            'count': len(scraped_jobs),
            'results': scraped_jobs
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Failed to fetch BrightData jobs'
        }, status=500)