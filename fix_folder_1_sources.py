#!/usr/bin/env python
"""
Create the missing SourceFolder ID 1 with proper TrackSource entries for Nike
This will fix the "System scraper error: No sources found in folder 1" issue
"""

import os
import sys
import django

# Add backend directory to Python path
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from track_accounts.models import SourceFolder, TrackSource
from users.models import Project

def create_folder_1_with_sources():
    print("🔧 CREATING FOLDER 1 WITH NIKE SOURCES")
    print("=" * 50)
    
    try:
        # Get or create project 1 (Demo)
        project, created = Project.objects.get_or_create(
            id=1,
            defaults={
                'name': 'Demo',
                'description': 'Demo project with Nike sources'
            }
        )
        
        if created:
            print(f"✅ Created project 1: {project.name}")
        else:
            print(f"✅ Using existing project 1: {project.name}")
        
        # Get or create SourceFolder with ID 1
        folder, created = SourceFolder.objects.get_or_create(
            id=1,
            defaults={
                'name': 'Nike - 12/10/2025 23:13:07',
                'project_id': 1,
                'description': 'Nike sources for scraping'
            }
        )
        
        if created:
            print(f"✅ Created folder 1: {folder.name}")
        else:
            print(f"✅ Using existing folder 1: {folder.name}")
        
        # Create Nike Instagram source
        instagram_source, created = TrackSource.objects.get_or_create(
            id=1,
            defaults={
                'name': 'Nike',
                'platform': 'instagram',
                'folder': folder,
                'project': project,
                'instagram_link': 'https://www.instagram.com/nike/'
            }
        )
        
        if created:
            print(f"✅ Created Instagram source: {instagram_source.name}")
        else:
            print(f"✅ Updated Instagram source: {instagram_source.name}")
            instagram_source.platform = 'instagram'
            instagram_source.folder = folder
            instagram_source.project = project
            instagram_source.instagram_link = 'https://www.instagram.com/nike/'
            instagram_source.save()
        
        # Create Nike Facebook source  
        facebook_source, created = TrackSource.objects.get_or_create(
            id=2,
            defaults={
                'name': 'Nike',
                'platform': 'facebook', 
                'folder': folder,
                'project': project,
                'facebook_link': 'https://www.facebook.com/nike/'
            }
        )
        
        if created:
            print(f"✅ Created Facebook source: {facebook_source.name}")
        else:
            print(f"✅ Updated Facebook source: {facebook_source.name}")
            facebook_source.platform = 'facebook'
            facebook_source.folder = folder
            facebook_source.project = project
            facebook_source.facebook_link = 'https://www.facebook.com/nike/'
            facebook_source.save()
        
        print("\n🎯 VERIFICATION")
        print("-" * 30)
        
        # Verify the query that was failing
        sources = TrackSource.objects.filter(folder_id=1, folder__project_id=1)
        print(f"📊 Sources found in folder 1 with project 1: {sources.count()}")
        
        for source in sources:
            print(f"  ✅ {source.platform}: {source.name}")
            if source.platform == 'instagram':
                print(f"     Instagram: {source.instagram_link}")
            elif source.platform == 'facebook':
                print(f"     Facebook: {source.facebook_link}")
        
        print(f"\n✅ SUCCESS: Folder 1 now has {sources.count()} active sources")
        print("🚀 The AutomatedBatchScraper should now work!")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_folder_1_with_sources()
    if success:
        print("\n🎉 FIX COMPLETE: 'System scraper error: No sources found in folder 1' should be resolved!")