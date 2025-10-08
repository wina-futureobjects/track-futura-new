#!/usr/bin/env python3
"""
Script to fix track source connection to workflow system
"""

# Create a Django management command to connect track sources
management_command = '''
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from track_accounts.models import TrackAccountUpload
from workflow.models import InputCollection
from users.models import Platform, Service, PlatformService

def connect_track_sources():
    """Connect existing track sources to workflow system"""
    
    print("🔍 Checking existing track sources...")
    
    # Get all track account uploads
    track_sources = TrackAccountUpload.objects.all()
    print(f"Found {len(track_sources)} track sources")
    
    for track_source in track_sources:
        print(f"\\nProcessing: {track_source.name}")
        print(f"Platform: {track_source.platform}")
        print(f"URLs: {track_source.urls}")
        
        # Check if InputCollection already exists
        existing = InputCollection.objects.filter(
            name=track_source.name,
            project=track_source.project
        ).first()
        
        if existing:
            print(f"✅ InputCollection already exists: {existing.id}")
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
            
            print(f"✅ Created InputCollection: {input_collection.id}")
            
        except Exception as e:
            print(f"❌ Error creating InputCollection: {str(e)}")
    
    print("\\n🎯 Connection process complete!")

if __name__ == "__main__":
    connect_track_sources()
'''

with open('fix_track_source_connection.py', 'w') as f:
    f.write(management_command)

print("✅ Created fix_track_source_connection.py")
print("📋 This script will connect track sources to workflow system")