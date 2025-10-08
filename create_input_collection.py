
from workflow.models import InputCollection, Platform, Service, PlatformService
from track_accounts.models import TrackSource

# Get Nike IG track source
nike_source = TrackSource.objects.filter(name__icontains='nike').first()
print(f"Found Nike source: {nike_source}")

# Get or create platform and service
platform, created = Platform.objects.get_or_create(
    name='Instagram',
    defaults={'description': 'Instagram platform'}
)
print(f"Platform: {platform} (created: {created})")

service, created = Service.objects.get_or_create(
    name='Posts',
    defaults={'description': 'Posts scraping service'}
)
print(f"Service: {service} (created: {created})")

platform_service, created = PlatformService.objects.get_or_create(
    platform=platform,
    service=service,
    defaults={'is_active': True}
)
print(f"PlatformService: {platform_service} (created: {created})")

# Create InputCollection
input_collection, created = InputCollection.objects.get_or_create(
    name='Nike Instagram Collection',
    defaults={
        'description': 'Nike Instagram for BrightData workflow',
        'project_id': 3,
        'platform_service': platform_service,
        'is_active': True,
        'metadata': {
            'track_source_id': nike_source.id if nike_source else None,
            'instagram_url': 'https://www.instagram.com/nike',
            'brightdata_ready': True
        }
    }
)

print(f"InputCollection created: {input_collection} (created: {created})")
print(f"InputCollection ID: {input_collection.id}")

# Verify
total_collections = InputCollection.objects.count()
print(f"Total InputCollections: {total_collections}")

# List all collections
for collection in InputCollection.objects.all():
    print(f"  - {collection.name} (ID: {collection.id}, Active: {collection.is_active})")
