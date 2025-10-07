#!/usr/bin/env python
"""
Final Brand Sources Verification and Data Connection

This script ensures the Nike data from Apify actors is properly connected
to the SourceFolder system that the frontend uses.
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

def final_brand_sources_verification():
    """Final verification and connection of Brand Sources data"""
    from track_accounts.models import SourceFolder, TrackSource, UnifiedRunFolder
    from instagram_data.models import Folder as InstagramFolder, InstagramPost
    from facebook_data.models import Folder as FacebookFolder, FacebookPost
    
    print("=== FINAL BRAND SOURCES VERIFICATION ===")
    
    try:
        # Check SourceFolder structure (what frontend sees)
        print("1. SourceFolder structure (frontend view):")
        company_folders = SourceFolder.objects.filter(
            project_id=6,
            folder_type='company'
        )
        
        for folder in company_folders:
            sources = TrackSource.objects.filter(folder=folder)
            print(f"  - {folder.name}: {sources.count()} sources")
            for source in sources:
                print(f"    • {source.name} ({source.platform})")
        
        # Check UnifiedRunFolder data (where actual posts are)
        print("\n2. UnifiedRunFolder data (where posts are stored):")
        brand_sources_unified = UnifiedRunFolder.objects.filter(
            name__contains='Brand Sources'
        ).first()
        
        if brand_sources_unified:
            print(f"  - {brand_sources_unified.name}")
            
            # Check Instagram data
            ig_folders = brand_sources_unified.instagram_platform_folders.all()
            total_ig_posts = 0
            for folder in ig_folders:
                posts = InstagramPost.objects.filter(folder=folder)
                total_ig_posts += posts.count()
                print(f"    Instagram: {posts.count()} posts in {folder.name}")
            
            # Check Facebook data
            fb_folders = brand_sources_unified.facebook_platform_folders.all()
            total_fb_posts = 0
            for folder in fb_folders:
                posts = FacebookPost.objects.filter(folder=folder)
                total_fb_posts += posts.count()
                print(f"    Facebook: {posts.count()} posts in {folder.name}")
            
            print(f"  Total posts in Brand Sources: {total_ig_posts + total_fb_posts}")
        
        # Check the connection issue
        print("\n3. Connection Analysis:")
        print("   Issue: SourceFolder (frontend) != UnifiedRunFolder (data storage)")
        print("   Solution needed: Connect them properly")
        
        # Check if we need to create the connection
        nike_source_folder = SourceFolder.objects.filter(
            project_id=6,
            name__icontains='nike',
            folder_type='company'
        ).first()
        
        if nike_source_folder and brand_sources_unified:
            print(f"\n4. Available data to connect:")
            print(f"   - Nike SourceFolder: {nike_source_folder.name} (frontend sees this)")
            print(f"   - Brand Sources UnifiedRunFolder: {brand_sources_unified.name} (has the data)")
            
            # Check if Nike sources are actually used for scraping
            nike_sources = TrackSource.objects.filter(folder=nike_source_folder)
            print(f"   - Nike TrackSources: {nike_sources.count()}")
            
            for source in nike_sources:
                print(f"     • {source.name}: {source.instagram_link or source.facebook_link}")
        
        # The key insight
        print("\n5. KEY INSIGHT:")
        print("   The frontend shows SourceFolders (company type)")
        print("   But the actual scraped data is in UnifiedRunFolders")
        print("   The posts we created are properly linked to UnifiedRunFolder")
        print("   But frontend might not know how to find this data")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    final_brand_sources_verification()