import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apify_integration.models import ApifyScraperRequest
from apify_integration.views import _process_apify_results

print('Processing Request ID 32...')
req = ApifyScraperRequest.objects.get(id=32)
print(f'Platform: {req.platform}')
print(f'Status: {req.status}')
print(f'Request ID: {req.request_id}')

try:
    _process_apify_results(req)
    print('[OK] Results processed successfully')
except Exception as e:
    print(f'[ERROR] {e}')
    import traceback
    traceback.print_exc()

# Check if data was saved
from facebook_data.models import Folder as FBFolder, FacebookPost
print('\nFacebook folders:', FBFolder.objects.filter(project_id=6).count())
print('Facebook posts:', FacebookPost.objects.filter(folder__project_id=6).count())
