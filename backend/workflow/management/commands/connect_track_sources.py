from django.core.management.base import BaseCommand
from track_accounts.models import TrackAccountUpload
from workflow.models import InputCollection
from users.models import Platform, Service, PlatformService

class Command(BaseCommand):
    help = 'Connect track sources to workflow system'

    def handle(self, *args, **options):
        self.stdout.write("Checking existing track sources...")
        
        # Get all track account uploads
        track_sources = TrackAccountUpload.objects.all()
        self.stdout.write(f"Found {len(track_sources)} track sources")
        
        for track_source in track_sources:
            self.stdout.write(f"\nProcessing: {track_source.name}")
            self.stdout.write(f"Platform: {track_source.platform}")
            
            # Check if InputCollection already exists
            existing = InputCollection.objects.filter(
                name=track_source.name,
                project=track_source.project
            ).first()
            
            if existing:
                self.stdout.write(f"InputCollection already exists: {existing.id}")
                continue
                
            # Get platform and service
            try:
                platform = Platform.objects.get(name=track_source.platform.lower())
                service = Service.objects.get(name='posts')  # Default to posts
                platform_service = PlatformService.objects.get(
                    platform=platform, 
                    service=service,
                    is_enabled=True
                )
                
                # Create InputCollection
                input_collection = InputCollection.objects.create(
                    name=track_source.name,
                    project=track_source.project,
                    platform_service=platform_service,
                    urls=track_source.urls,
                    description=f"Auto-created from track source: {track_source.name}",
                    status='active'
                )
                
                self.stdout.write(self.style.SUCCESS(f"Created InputCollection: {input_collection.id}"))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creating InputCollection: {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS("\nConnection process complete!"))