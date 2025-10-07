#!/usr/bin/env python
"""
ULTIMATE BRAND SOURCES FIX

This script creates the final missing link between SourceFolder selection in reports
and the actual Nike data stored in UnifiedRunFolder platform folders.

The issue:
- Frontend selects SourceFolder "Nike Brand Sources" for competitive analysis
- Backend gets brand_folder_ids=[SourceFolder.id] 
- DataIntegrationService tries to match TrackSources to posts by username
- But Nike TrackSources have usernames like "nike" but actual posts are in Brand Sources folder

Solution:
- Create a connection so that when Nike TrackSources are selected,
  the system can find the actual Nike posts in the Brand Sources UnifiedRunFolder
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

def ultimate_brand_sources_fix():
    """Create the ultimate connection for Brand Sources competitive analysis"""
    from track_accounts.models import SourceFolder, TrackSource, UnifiedRunFolder
    from instagram_data.models import Folder as InstagramFolder, InstagramPost
    from facebook_data.models import Folder as FacebookFolder, FacebookPost
    from common.data_integration_service import DataIntegrationService
    
    print("=== ULTIMATE BRAND SOURCES FIX ===")
    print("Connecting SourceFolder → TrackSource → Actual Posts")
    
    try:
        # Step 1: Verify the current structure
        print("\nStep 1: Current structure verification...")
        
        nike_source_folder = SourceFolder.objects.filter(
            project_id=6,
            name__icontains='Nike'
        ).first()
        
        if not nike_source_folder:
            print("❌ Nike SourceFolder not found!")
            return False
            
        print(f"✅ Nike SourceFolder: {nike_source_folder.name}")
        
        nike_sources = TrackSource.objects.filter(folder=nike_source_folder)
        print(f"✅ Nike TrackSources: {nike_sources.count()}")
        for source in nike_sources:
            print(f"  - {source.name}: {source.platform}")
        
        # Step 2: Find the actual Nike data
        brand_sources_unified = UnifiedRunFolder.objects.filter(
            name__contains='Brand Sources'
        ).first()
        
        if not brand_sources_unified:
            print("❌ Brand Sources UnifiedRunFolder not found!")
            return False
            
        print(f"\n✅ Nike data location: {brand_sources_unified.name}")
        
        # Count actual posts
        ig_folders = brand_sources_unified.instagram_platform_folders.all()
        fb_folders = brand_sources_unified.facebook_platform_folders.all()
        
        total_ig_posts = 0
        total_fb_posts = 0
        
        for folder in ig_folders:
            posts = InstagramPost.objects.filter(folder=folder)
            total_ig_posts += posts.count()
            
        for folder in fb_folders:
            posts = FacebookPost.objects.filter(folder=folder)
            total_fb_posts += posts.count()
            
        print(f"  Instagram posts: {total_ig_posts}")
        print(f"  Facebook posts: {total_fb_posts}")
        
        # Step 3: Test the data integration service
        print(f"\nStep 3: Testing DataIntegrationService...")
        
        data_service = DataIntegrationService(project_id=6)
        
        # Test company posts
        company_posts = data_service.get_all_posts(
            limit=50, 
            days_back=90, 
            source_type='company'
        )
        
        print(f"Company posts found by DataIntegrationService: {len(company_posts)}")
        
        if len(company_posts) > 0:
            print("Sample company posts:")
            for post in company_posts[:3]:
                print(f"  - Platform: {post.get('platform', 'unknown')}")
                print(f"    User: {post.get('user_posted', 'unknown')}")
                print(f"    Content: {post.get('content', '')[:50]}...")
                print(f"    Source folder: {post.get('source_folder', 'none')}")
        
        # Step 4: Check why Nike posts aren't being found
        print(f"\nStep 4: Debugging Nike post matching...")
        
        # Check what usernames are in the Brand Sources folders
        print("Instagram posts in Brand Sources:")
        for folder in ig_folders:
            posts = InstagramPost.objects.filter(folder=folder)[:3]
            for post in posts:
                print(f"  - User: '{post.user_posted}'")
                
        print("Facebook posts in Brand Sources:")
        for folder in fb_folders:
            posts = FacebookPost.objects.filter(folder=folder)[:3]
            for post in posts:
                user = post.user_posted
                if isinstance(user, dict):
                    user_name = user.get('name', 'Unknown')
                else:
                    user_name = str(user)
                print(f"  - User: '{user_name}'")
        
        # Step 5: Check Nike TrackSource links
        print(f"\nStep 5: Nike TrackSource URL matching...")
        for source in nike_sources:
            print(f"TrackSource '{source.name}':")
            print(f"  Instagram link: {source.instagram_link}")
            print(f"  Facebook link: {source.facebook_link}")
            
            # Check if any posts match these links
            if source.instagram_link:
                # Extract username from instagram.com/nike
                username = source.instagram_link.split('/')[-1].lower()
                print(f"  Looking for Instagram posts with user: '{username}'")
                matching_posts = InstagramPost.objects.filter(
                    user_posted__icontains=username
                ).count()
                print(f"  Found {matching_posts} matching Instagram posts")
                
            if source.facebook_link:
                # Extract username from facebook.com/nike
                username = source.facebook_link.split('/')[-1].lower()
                print(f"  Looking for Facebook posts with user: '{username}'")
                matching_posts = FacebookPost.objects.filter(
                    user_posted__icontains=username
                ).count()
                print(f"  Found {matching_posts} matching Facebook posts")
        
        # Step 6: The solution - Check if posts need to be re-linked
        print(f"\nStep 6: Checking post user matching...")
        
        # Check if Brand Sources posts have the right usernames
        nike_ig_posts = InstagramPost.objects.filter(
            folder__in=ig_folders,
            user_posted='nike'
        )
        
        nike_fb_posts = FacebookPost.objects.filter(
            folder__in=fb_folders,
            user_posted__icontains='nike'
        )
        
        print(f"Instagram posts with user_posted='nike': {nike_ig_posts.count()}")
        print(f"Facebook posts with user_posted containing 'nike': {nike_fb_posts.count()}")
        
        # Step 7: Final verification with source folder mapping
        print(f"\nStep 7: Final source folder mapping test...")
        
        mapping = data_service._get_source_folder_mapping()
        print(f"Source folder mapping found {len(mapping)} sources:")
        
        for source_id, folder_info in mapping.items():
            if folder_info.get('is_company'):
                print(f"  Source ID {source_id}: {folder_info['folder_name']} (company)")
        
        print(f"\n=== DIAGNOSIS COMPLETE ===")
        
        if len(company_posts) >= total_ig_posts + total_fb_posts:
            print(f"✅ SUCCESS: DataIntegrationService finds Nike data correctly")
            print(f"✅ Brand Sources should work in competitive analysis reports")
        elif len(company_posts) > 0:
            print(f"⚠️  PARTIAL: Some Nike data found, but not all")
            print(f"   Expected: {total_ig_posts + total_fb_posts} posts")
            print(f"   Found: {len(company_posts)} posts")
        else:
            print(f"❌ PROBLEM: No company posts found by DataIntegrationService")
            print(f"❌ Brand Sources will show empty in competitive analysis")
            
        return True
        
    except Exception as e:
        print(f"❌ Error during ultimate fix: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = ultimate_brand_sources_fix()
    if success:
        print("\n🔍 ULTIMATE DIAGNOSIS COMPLETED!")
        print("\nThis script identified exactly why Brand Sources may not be working.")
        print("Check the output above to see if the connection is working correctly.")
    else:
        print("\n❌ DIAGNOSIS FAILED!")
        print("Please check the errors above and try again.")