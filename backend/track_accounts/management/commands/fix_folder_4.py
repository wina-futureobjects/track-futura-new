from django.core.management.base import BaseCommand
from track_accounts.models import SourceFolder, TrackSource
from datetime import datetime


class Command(BaseCommand):
    help = 'Fix folder 4 sources for scraper'

    def handle(self, *args, **options):
        self.stdout.write("🔧 Fixing folder 4 sources...")
        
        try:
            # Create folder 4 if it doesn't exist
            folder_4, created = SourceFolder.objects.get_or_create(
                id=4,
                project_id=1,
                defaults={
                    'name': 'Nike - Complete Social Media Collection V2',
                    'description': 'Nike social media collection for folder 4',
                    'folder_type': 'company',
                    'created_at': datetime.now()
                }
            )
            
            if created:
                self.stdout.write(f"✅ Created folder 4: {folder_4.name}")
            else:
                self.stdout.write(f"✅ Folder 4 exists: {folder_4.name}")
            
            # Check existing sources
            existing_sources = TrackSource.objects.filter(folder_id=4, folder__project_id=1)
            
            if existing_sources.count() == 0:
                # Create sources
                sources_data = [
                    {'name': 'Nike Instagram (F4)', 'platform': 'instagram', 'username': 'nike'},
                    {'name': 'Nike Facebook (F4)', 'platform': 'facebook', 'username': 'nike'},
                    {'name': 'Adidas Instagram (F4)', 'platform': 'instagram', 'username': 'adidas'},
                ]
                
                for source_data in sources_data:
                    source = TrackSource.objects.create(
                        name=source_data['name'],
                        platform=source_data['platform'],
                        username=source_data['username'],
                        folder_id=4,
                        is_active=True,
                        created_at=datetime.now()
                    )
                    self.stdout.write(f"✅ Created: {source.name}")
            else:
                self.stdout.write(f"✅ Folder 4 already has {existing_sources.count()} sources")
            
            # Final verification
            final_count = TrackSource.objects.filter(folder_id=4, folder__project_id=1).count()
            self.stdout.write(f"🎯 Folder 4 now has {final_count} sources - Ready for scraping!")
            
        except Exception as e:
            self.stdout.write(f"❌ Error: {str(e)}")
            raise