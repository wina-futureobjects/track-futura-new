import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apify_integration.models import ApifyScraperRequest
from apify_integration.views import _process_apify_results

print('=== PROCESSING INSTAGRAM REQUEST 31 ===\n')

req = ApifyScraperRequest.objects.get(id=31)
print(f'Request ID: {req.id}')
print(f'Platform: {req.platform}')
print(f'Source: {req.source_name}')
print(f'Apify Request ID: {req.request_id}')
print(f'Status: {req.status}')
print(f'Error Message: {req.error_message}')

print('\nProcessing results...')
try:
    _process_apify_results(req)
    print('[OK] Results processed successfully')
except Exception as e:
    print(f'[ERROR] {e}')
    import traceback
    traceback.print_exc()
