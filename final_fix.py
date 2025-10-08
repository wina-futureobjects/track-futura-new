
# Use correct model imports
from workflow.models import InputCollection, PlatformService
from track_accounts.models import TrackSource

# Get Nike source
nike_source = TrackSource.objects.filter(name__icontains='nike').first()
print(f"Nike source: {nike_source}")

# Check existing platform services
platform_services = PlatformService.objects.all()
print(f"PlatformServices count: {platform_services.count()}")

for ps in platform_services:
    print(f"  - PlatformService ID {ps.id}: {ps}")

if platform_services.exists():
    # Use the first platform service
    ps = platform_services.first()
    print(f"Using PlatformService: {ps}")
    
    # Create InputCollection
    ic = InputCollection.objects.create(
        project_id=3,
        platform_service=ps,
        urls=['https://www.instagram.com/nike'],
        status='active'
    )
    print(f"SUCCESS! Created InputCollection ID: {ic.id}")
    
    # Verify
    total = InputCollection.objects.count()
    print(f"Total InputCollections now: {total}")
    
    # Show all collections
    for collection in InputCollection.objects.all():
        print(f"  - Collection ID {collection.id}, Project {collection.project_id}, Status: {collection.status}")
        
else:
    print("ERROR: No PlatformServices found")
