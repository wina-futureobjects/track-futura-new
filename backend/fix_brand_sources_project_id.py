#!/usr/bin/env python
"""
FINAL FIX: Update Brand Sources Platform Folders Project ID

This script fixes the project_id on Brand Sources platform folders so that
DataIntegrationService can find Nike posts for competitive analysis.
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

def fix_brand_sources_project_id():
    """Fix the project_id on Brand Sources platform folders"""
    from track_accounts.models import UnifiedRunFolder
    from instagram_data.models import Folder as InstagramFolder, InstagramPost
    from facebook_data.models import Folder as FacebookFolder, FacebookPost
    from common.data_integration_service import DataIntegrationService
    
    print("=== FIXING BRAND SOURCES PROJECT ID ===")
    
    try:
        # Get Brand Sources unified folder
        brand_sources = UnifiedRunFolder.objects.filter(
            name__contains='Brand Sources'
        ).first()
        
        print(f"Brand Sources UnifiedRunFolder:")
        print(f"  Name: {brand_sources.name}")
        print(f"  Project ID: {brand_sources.project_id}")
        
        # Get Nike platform folders
        ig_folders = brand_sources.instagram_platform_folders.all()
        fb_folders = brand_sources.facebook_platform_folders.all()
        
        print(f"\nFixing Instagram folders...")
        for folder in ig_folders:
            posts = InstagramPost.objects.filter(folder=folder)
            print(f"  - {folder.name}")
            print(f"    Before: project_id = {folder.project_id}")
            
            # Fix the project_id
            folder.project_id = brand_sources.project_id
            folder.save()
            
            print(f"    After: project_id = {folder.project_id}")
            print(f"    Posts: {posts.count()}")
        
        print(f"\nFixing Facebook folders...")
        for folder in fb_folders:
            posts = FacebookPost.objects.filter(folder=folder)
            print(f"  - {folder.name}")
            print(f"    Before: project_id = {folder.project_id}")
            
            # Fix the project_id
            folder.project_id = brand_sources.project_id
            folder.save()
            
            print(f"    After: project_id = {folder.project_id}")
            print(f"    Posts: {posts.count()}")
        
        print(f"\n=== VERIFICATION ===")
        
        # Test DataIntegrationService again
        print(f"Testing DataIntegrationService after fix...")
        
        data_service = DataIntegrationService(project_id=brand_sources.project_id)
        
        company_posts = data_service.get_all_posts(
            limit=50,
            days_back=90,
            source_type='company'
        )
        
        print(f"✅ Company posts found: {len(company_posts)}")
        
        if len(company_posts) > 0:
            print(f"Sample company posts:")
            for post in company_posts[:3]:
                print(f"  - Platform: {post.get('platform', 'unknown')}")
                print(f"    User: {post.get('user_posted', 'unknown')}")
                print(f"    Content: {post.get('content', '')[:50]}...")
                print(f"    Source folder: {post.get('source_folder', 'none')}")
        
        # Test competitive analysis simulation
        print(f"\nTesting competitive analysis data...")
        
        competitor_posts = data_service.get_all_posts(
            limit=50,
            days_back=90,
            source_type='competitor'
        )
        
        print(f"✅ Competitor posts found: {len(competitor_posts)}")
        
        print(f"\n=== SUCCESS VERIFICATION ===")
        
        if len(company_posts) > 0:
            print(f"🎉 SUCCESS! Brand Sources will now work in competitive analysis!")
            print(f"✅ Nike company data: {len(company_posts)} posts")
            print(f"✅ Competitor data: {len(competitor_posts)} posts")
            print(f"✅ DataIntegrationService can now find Nike posts")
            print(f"✅ Competitive Analysis reports will show Nike data")
        else:
            print(f"❌ Still not working. Additional debugging needed.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during fix: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_brand_sources_project_id()
    if success:
        print("\n🎉 BRAND SOURCES PROJECT ID FIX COMPLETED!")
        print("\nNow refresh your frontend and try generating a Competitive Analysis report.")
        print("Brand Sources should show Nike data instead of loading!")
    else:
        print("\n❌ FIX FAILED!")
        print("Please check the errors above and try again.")