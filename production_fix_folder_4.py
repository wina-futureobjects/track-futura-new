#!/usr/bin/env python3

import os
import sys
import django
from datetime import datetime

# Setup Django environment for production
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trackfutura.settings')
django.setup()

from track_accounts.models import SourceFolder, TrackSource

def fix_folder_4_production():
    """
    Create folder 4 with Nike sources in production database
    This fixes: System scraper error: No sources found in folder 4
    """
    
    print("🔧 PRODUCTION FIX: Creating Folder 4 with Nike Sources")
    print("=" * 60)
    
    try:
        # Check if folder 4 already exists
        try:
            existing_folder = SourceFolder.objects.get(id=4, project_id=1)
            print(f"✅ Folder 4 already exists: {existing_folder.name}")
        except SourceFolder.DoesNotExist:
            # Create folder 4
            folder_4 = SourceFolder.objects.create(
                id=4,
                name="Nike - Complete Social Media Collection V2",
                description="Nike social media collection including Instagram and Facebook sources for folder 4",
                project_id=1,
                created_at=datetime.now(),
                folder_type="company"
            )
            print(f"✅ Created folder 4: {folder_4.name}")
        
        # Check if sources exist in folder 4
        existing_sources = TrackSource.objects.filter(folder_id=4, folder__project_id=1)
        print(f"📊 Current sources in folder 4: {existing_sources.count()}")
        
        if existing_sources.count() == 0:
            print("🔧 Creating Nike sources in folder 4...")
            
            # Create Nike Instagram source
            instagram_source = TrackSource.objects.create(
                name="Nike Instagram (Folder 4)",
                platform="instagram",
                username="nike",
                folder_id=4,
                is_active=True,
                created_at=datetime.now()
            )
            print(f"✅ Created: {instagram_source.name}")
            
            # Create Nike Facebook source
            facebook_source = TrackSource.objects.create(
                name="Nike Facebook (Folder 4)",
                platform="facebook",
                username="nike",
                folder_id=4,
                is_active=True,
                created_at=datetime.now()
            )
            print(f"✅ Created: {facebook_source.name}")
            
            # Create additional sources to make it robust
            adidas_instagram = TrackSource.objects.create(
                name="Adidas Instagram (Folder 4)",
                platform="instagram",
                username="adidas",
                folder_id=4,
                is_active=True,
                created_at=datetime.now()
            )
            print(f"✅ Created: {adidas_instagram.name}")
            
        else:
            print("✅ Folder 4 already has sources:")
            for source in existing_sources:
                print(f"   - {source.name} ({source.platform})")
        
        # Final verification
        final_check = TrackSource.objects.filter(folder_id=4, folder__project_id=1)
        print(f"\n🎯 FINAL VERIFICATION:")
        print(f"   Folder 4 now has {final_check.count()} sources")
        
        if final_check.count() > 0:
            print("✅ SUCCESS: Folder 4 is ready for scraping!")
            print("\n📋 Sources in folder 4:")
            for source in final_check:
                print(f"   ✓ {source.name} ({source.platform}) - Active: {source.is_active}")
            return True
        else:
            print("❌ FAILED: Folder 4 still has no sources")
            return False
            
    except Exception as e:
        print(f"❌ ERROR in production fix: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def verify_all_folders():
    """Verify all folders have sources"""
    print("\n📊 FOLDER INVENTORY:")
    print("=" * 40)
    
    folders = SourceFolder.objects.filter(project_id=1).order_by('id')
    
    for folder in folders:
        sources_count = TrackSource.objects.filter(folder_id=folder.id, folder__project_id=1).count()
        status = "✅" if sources_count > 0 else "❌"
        print(f"{status} Folder {folder.id}: {folder.name} ({sources_count} sources)")

if __name__ == "__main__":
    print("🚀 PRODUCTION DATABASE FIX")
    print("Target: System scraper error: No sources found in folder 4")
    print("=" * 70)
    
    # Fix folder 4
    success = fix_folder_4_production()
    
    # Show all folders status
    verify_all_folders()
    
    if success:
        print("\n🎉 PRODUCTION FIX COMPLETE!")
        print("The 'System scraper error: No sources found in folder 4' should now be resolved!")
    else:
        print("\n❌ PRODUCTION FIX FAILED!")
        print("Manual intervention may be required.")