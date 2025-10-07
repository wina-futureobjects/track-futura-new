import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apify_integration.models import ApifyScraperRequest
import requests

print('=== PROCESSING PENDING SCRAPER REQUESTS ===\n')

# Get all processing requests
requests_to_process = ApifyScraperRequest.objects.filter(status='processing')

for req in requests_to_process:
    print(f'Request ID: {req.id}')
    print(f'Platform: {req.platform}')
    print(f'Source: {req.source_name}')
    print(f'Request ID (Apify): {req.request_id}')
    print(f'Status: {req.status}')

    if not req.request_id:
        print('  [X] No Apify request_id - cannot process')
        print('---\n')
        continue

    # Try to fetch results from Apify
    try:
        from apify_integration.views import _process_apify_results

        # Mark as completed
        req.status = 'completed'
        req.save()

        # Process results
        print(f'  [OK] Processing results for request {req.request_id}...')
        _process_apify_results(req)
        print(f'  [OK] Results processed successfully')

    except Exception as e:
        print(f'  [ERROR] Error processing results: {e}')
        import traceback
        traceback.print_exc()
        req.status = 'failed'
        req.error_message = str(e)
        req.save()

    print('---\n')

print('=== DONE ===')
