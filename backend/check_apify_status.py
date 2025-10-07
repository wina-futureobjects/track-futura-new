import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apify_integration.models import ApifyBatchJob, ApifyScraperRequest, ApifyWebhookEvent

print('=== SCRAPER REQUEST 30 (Instagram) ===')
req30 = ApifyScraperRequest.objects.get(id=30)
print(f'Platform: {req30.platform}')
print(f'Status: {req30.status}')
print(f'Run ID: {req30.run_id}')
print(f'Dataset ID: {req30.dataset_id}')
print(f'Completed At: {req30.completed_at}')

print('\n=== SCRAPER REQUEST 31 (Facebook) ===')
req31 = ApifyScraperRequest.objects.get(id=31)
print(f'Platform: {req31.platform}')
print(f'Status: {req31.status}')
print(f'Run ID: {req31.run_id}')
print(f'Dataset ID: {req31.dataset_id}')
print(f'Completed At: {req31.completed_at}')

print('\n=== WEBHOOK EVENTS ===')
for event in ApifyWebhookEvent.objects.filter(resource__resource_id__in=[req30.run_id, req31.run_id]):
    print(f'Run ID: {event.resource.get("resource_id")}')
    print(f'Event Type: {event.event_type}')
    print(f'Status: {event.resource.get("status")}')
    print(f'Created: {event.created_at}')
    print('---')
