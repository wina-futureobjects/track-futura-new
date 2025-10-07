#!/usr/bin/env python
"""
CAREFUL FIX for Brand Sources Issue

This script carefully analyzes and fixes the Brand Sources display issue
by understanding exactly what the frontend expects.
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

def careful_brand_sources_fix():
    """Carefully fix Brand Sources by creating the exact structure frontend expects"""
    from track_accounts.models import SourceFolder, TrackSource
    
    print("=== CAREFUL BRAND SOURCES FIX ===")
    
    try:
        # Step 1: Check current SourceFolders in project 6
        print("Step 1: Checking current SourceFolders...")
        project_6_folders = SourceFolder.objects.filter(project_id=6)
        print(f"SourceFolders in project 6: {project_6_folders.count()}")
        
        for folder in project_6_folders:
            sources_count = TrackSource.objects.filter(folder=folder).count()
            print(f"  - {folder.name} (Type: {folder.folder_type}): {sources_count} sources")
        
        # Step 2: Check if Nike company folder exists
        print("\nStep 2: Checking for Nike company folder...")
        nike_company_folder = project_6_folders.filter(
            folder_type='company',
            name__icontains='nike'
        ).first()
        
        if nike_company_folder:
            print(f"✅ Nike company folder exists: {nike_company_folder.name}")
        else:
            print("❌ No Nike company folder found")
            
            # Create Nike company folder
            print("Creating Nike company folder...")
            nike_company_folder = SourceFolder.objects.create(
                name="Nike Brand Sources",
                description="Nike official brand social media sources",
                folder_type='company',
                project_id=6
            )
            print(f"✅ Created Nike company folder: {nike_company_folder.name}")
        
        # Step 3: Get Nike sources and link them to company folder
        print("\nStep 3: Linking Nike sources to company folder...")
        nike_sources = TrackSource.objects.filter(
            project_id=6,
            name__icontains='nike'
        )
        
        print(f"Found {nike_sources.count()} Nike sources:")
        for source in nike_sources:
            print(f"  - {source.name}: {source.platform}")
            
            # Link to Nike company folder
            if source.folder != nike_company_folder:
                source.folder = nike_company_folder
                source.save()
                print(f"    ✅ Linked to Nike company folder")
            else:
                print(f"    ✅ Already linked to Nike company folder")
        
        # Step 4: Verify the fix
        print("\nStep 4: Verifying the fix...")
        
        # Check company folders in project 6
        company_folders = SourceFolder.objects.filter(
            project_id=6,
            folder_type='company'
        )
        print(f"Company folders in project 6: {company_folders.count()}")
        
        for folder in company_folders:
            sources_count = TrackSource.objects.filter(folder=folder).count()
            print(f"  - {folder.name}: {sources_count} sources")
            
            # Show sources in this folder
            sources = TrackSource.objects.filter(folder=folder)
            for source in sources:
                print(f"    • {source.name} ({source.platform})")
        
        # Step 5: Check what frontend will see
        print("\nStep 5: Frontend verification...")
        print("The frontend will now see:")
        print(f"  - Brand Sources: {company_folders.count()} company folders")
        print(f"  - Nike sources available in company folder")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during careful fix: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = careful_brand_sources_fix()
    if success:
        print("\n🎉 CAREFUL FIX COMPLETED!")
        print("\nThe Brand Sources should now appear correctly in the frontend.")
        print("Frontend will find company folders with Nike sources linked to them.")
    else:
        print("\n❌ CAREFUL FIX FAILED!")
        print("Please check the errors above and try again.")