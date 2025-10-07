import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apify_integration.models import ApifyBatchJob, ApifyScraperRequest

batch = ApifyBatchJob.objects.filter(project_id=6).order_by('-created_at').first()
print(f'Latest Batch Job: {batch.id}')
print(f'Name: {batch.name}')
print(f'Status: {batch.status}')
print(f'Created: {batch.created_at}')
print()
print('Scraper Requests:')
for req in batch.scraper_requests.all():
    print(f'  - ID: {req.id}, Platform: {req.platform}, Status: {req.status}')
    print(f'    Request ID: {req.request_id}')
    print(f'    Source: {req.source_name}')
