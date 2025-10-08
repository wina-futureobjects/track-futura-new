
# Check workflow models
import workflow.models
print("Workflow models:", [name for name in dir(workflow.models) if not name.startswith('_')])

# Get Nike source
from track_accounts.models import TrackSource
nike_source = TrackSource.objects.filter(name__icontains='nike').first()
print(f"Nike source: {nike_source}")

# Check existing InputCollections
from workflow.models import InputCollection
existing = InputCollection.objects.count()
print(f"Existing InputCollections: {existing}")

# Check InputCollection fields
print("InputCollection fields:", [f.name for f in InputCollection._meta.fields])

# Check PlatformService
try:
    from brightdata_integration.models import PlatformService
    platform_services = PlatformService.objects.all()
    print(f"PlatformServices count: {platform_services.count()}")
    if platform_services.exists():
        ps = platform_services.first()
        print(f"First PlatformService: {ps}")
        
        # Create InputCollection
        ic = InputCollection.objects.create(
            name='Nike Instagram Collection',
            description='Nike Instagram for workflow',
            project_id=3,
            platform_service=ps,
            is_active=True
        )
        print(f"Created InputCollection: {ic.id}")
        
        # Verify
        total = InputCollection.objects.count()
        print(f"Total InputCollections now: {total}")
        
except Exception as e:
    print(f"Error: {e}")
