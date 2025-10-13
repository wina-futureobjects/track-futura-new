#!/usr/bin/env python
"""
Debug the exact query that's failing in trigger_scraper_from_system
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

from track_accounts.models import TrackSource, SourceFolder

def debug_folder_1_sources():
    print("🔍 DEBUGGING FOLDER 1 SOURCES QUERY")
    print("=" * 50)
    
    # This is the exact query from the service that's failing
    folder_id = 1
    
    print(f"📁 Query: TrackSource.objects.filter(folder_id={folder_id}, folder__project_id=1)")
    sources = TrackSource.objects.filter(folder_id=folder_id, folder__project_id=1)
    print(f"📊 Result count: {sources.count()}")
    
    if sources.exists():
        for source in sources:
            print(f"  ✅ Source ID {source.id}: {source.name} ({source.platform})")
            print(f"     Folder ID: {source.folder_id}")
            print(f"     Project ID: {source.folder.project_id if source.folder else 'None'}")
    else:
        print("❌ NO SOURCES FOUND")
    
    print("\n🔍 Let's check all sources in folder 1:")
    all_folder_1_sources = TrackSource.objects.filter(folder_id=folder_id)
    print(f"📊 All sources in folder 1: {all_folder_1_sources.count()}")
    
    for source in all_folder_1_sources:
        print(f"  📋 Source ID {source.id}: {source.name} ({source.platform})")
        print(f"     Folder ID: {source.folder_id}")
        if source.folder:
            print(f"     Project ID: {source.folder.project_id}")
        else:
            print(f"     Folder: None (orphaned source)")
        print(f"     Links: IG={bool(source.instagram_link)}, FB={bool(source.facebook_link)}")
    
    print("\n🔍 Let's check the folder itself:")
    try:
        folder = SourceFolder.objects.get(id=folder_id)
        print(f"  📂 Folder ID {folder.id}: {folder.name}")
        print(f"     Project ID: {folder.project_id}")
        print(f"     Created: {folder.created_at}")
    except SourceFolder.DoesNotExist:
        print(f"❌ Folder {folder_id} does not exist!")
    
    print("\n🔍 Let's check all projects:")
    from users.models import Project
    projects = Project.objects.all()
    for project in projects:
        print(f"  🎯 Project ID {project.id}: {project.name}")

if __name__ == "__main__":
    debug_folder_1_sources()