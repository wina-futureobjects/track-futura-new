#!/usr/bin/env python
"""
Diagnose Brand Sources Frontend Issue

This script investigates why the Brand Sources data might not be
appearing in the frontend despite being linked correctly.
"""

import os
import sys
import django

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def diagnose_brand_sources_issue():
    """Diagnose why Brand Sources data is not appearing in frontend"""
    from track_accounts.models import UnifiedRunFolder, TrackSource
    from instagram_data.models import Folder as InstagramFolder, InstagramPost
    from facebook_data.models import Folder as FacebookFolder, FacebookPost
    
    print("=== BRAND SOURCES FRONTEND DIAGNOSIS ===")
    
    try:
        # Get Brand Sources folder
        brand_sources = UnifiedRunFolder.objects.filter(name__contains='Brand Sources').first()
        if not brand_sources:
            print("❌ Brand Sources folder not found!")
            return False
            
        print(f"✅ Brand Sources: {brand_sources.name}")
        print(f"   ID: {brand_sources.id}")
        print(f"   Project: {brand_sources.project_id}")
        print(f"   Type: {brand_sources.folder_type}")
        
        # Check platform folders
        ig_folders = brand_sources.instagram_platform_folders.all()
        fb_folders = brand_sources.facebook_platform_folders.all()
        
        print(f"\n=== PLATFORM FOLDERS STATUS ===")
        print(f"Instagram folders: {ig_folders.count()}")
        for folder in ig_folders:
            posts = InstagramPost.objects.filter(folder=folder)
            print(f"  - {folder.name}: {posts.count()} posts")
            print(f"    ID: {folder.id}, Type: {folder.folder_type}, Category: {folder.category}")
            
        print(f"Facebook folders: {fb_folders.count()}")
        for folder in fb_folders:
            posts = FacebookPost.objects.filter(folder=folder)
            print(f"  - {folder.name}: {posts.count()} posts")
            print(f"    ID: {folder.id}, Type: {folder.folder_type}, Category: {folder.category}")
        
        # Check if folder types match what frontend expects
        print(f"\n=== FRONTEND COMPATIBILITY CHECK ===")
        
        # Frontend typically looks for 'company' type folders for brand sources
        if brand_sources.folder_type != 'run':
            print(f"⚠️  Brand Sources type is '{brand_sources.folder_type}', frontend might expect 'run'")
        else:
            print(f"✅ Brand Sources type is correct: '{brand_sources.folder_type}'")
        
        # Check if we need to create 'company' type subfolders
        company_folders = UnifiedRunFolder.objects.filter(
            parent_folder=brand_sources,
            folder_type='company'
        )
        print(f"Company subfolders under Brand Sources: {company_folders.count()}")
        
        if company_folders.count() == 0:
            print("⚠️  No 'company' type subfolders found - frontend might be looking for these")
        
        # Check project association
        print(f"\n=== PROJECT ASSOCIATION ===")
        project_sources = TrackSource.objects.filter(project_id=brand_sources.project_id)
        print(f"TrackSources in project {brand_sources.project_id}: {project_sources.count()}")
        
        for source in project_sources:
            print(f"  - {source.name}: {source.platform} ({source.service_name})")
        
        # Check if there are Nike sources specifically
        nike_sources = project_sources.filter(name__icontains='nike')
        print(f"Nike sources in project: {nike_sources.count()}")
        
        # Suggest solution
        print(f"\n=== POTENTIAL SOLUTION ===")
        
        if company_folders.count() == 0:
            print("Issue likely: Frontend expects 'company' type folders under Brand Sources")
            print("Solution: Create Nike company folder and link data to it")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during diagnosis: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    diagnose_brand_sources_issue()