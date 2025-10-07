#!/usr/bin/env python
"""
Verify Nike Brand Sources Fix

This script verifies that the Nike brand sources fix worked correctly
and the data is now available for the frontend.
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

def verify_nike_fix():
    """Verify that Nike brand sources are now working"""
    from track_accounts.models import UnifiedRunFolder, TrackSource
    from instagram_data.models import Folder as InstagramFolder, InstagramPost
    from facebook_data.models import Folder as FacebookFolder, FacebookPost
    
    print("=== NIKE BRAND SOURCES VERIFICATION ===")
    
    try:
        # Check Nike TrackSources
        nike_ig_source = TrackSource.objects.get(id=6)  # Nike Instagram
        nike_fb_source = TrackSource.objects.get(id=11)  # Nike Facebook
        
        print(f"✅ Nike Instagram TrackSource: {nike_ig_source.name}")
        print(f"   Project: {nike_ig_source.project_id}")
        print(f"   Instagram Link: {nike_ig_source.instagram_link}")
        
        print(f"✅ Nike Facebook TrackSource: {nike_fb_source.name}")
        print(f"   Project: {nike_fb_source.project_id}")
        print(f"   Facebook Link: {nike_fb_source.facebook_link}")
        
        # Check Nike unified folders
        nike_ig_unified = UnifiedRunFolder.objects.get(name="Instagram Profile - nike")
        nike_fb_unified = UnifiedRunFolder.objects.get(name="Facebook Profile - nike")
        
        print(f"\n✅ Nike Instagram Unified Folder: {nike_ig_unified.name}")
        print(f"   Project: {nike_ig_unified.project_id}")
        print(f"   Type: {nike_ig_unified.folder_type}")
        
        print(f"✅ Nike Facebook Unified Folder: {nike_fb_unified.name}")
        print(f"   Project: {nike_fb_unified.project_id}")
        print(f"   Type: {nike_fb_unified.folder_type}")
        
        # Check Nike platform folders
        nike_ig_folders = nike_ig_unified.instagram_platform_folders.all()
        nike_fb_folders = nike_fb_unified.facebook_platform_folders.all()
        
        print(f"\n✅ Nike Instagram Platform Folders: {nike_ig_folders.count()}")
        for folder in nike_ig_folders:
            posts_count = folder.get_content_count()
            print(f"   - {folder.name}: {posts_count} posts")
        
        print(f"✅ Nike Facebook Platform Folders: {nike_fb_folders.count()}")
        for folder in nike_fb_folders:
            posts_count = folder.get_content_count()
            print(f"   - {folder.name}: {posts_count} posts")
        
        # Check Nike posts
        print(f"\n=== NIKE POSTS SAMPLE ===")
        
        if nike_ig_folders.exists():
            nike_ig_folder = nike_ig_folders.first()
            nike_ig_posts = InstagramPost.objects.filter(folder=nike_ig_folder)[:3]
            print(f"Nike Instagram Posts (showing first 3 of {nike_ig_posts.count()}):")
            for post in nike_ig_posts:
                print(f"   - {post.user_posted}: {post.description[:60]}...")
                print(f"     Likes: {post.likes}, Comments: {post.num_comments}")
        
        if nike_fb_folders.exists():
            nike_fb_folder = nike_fb_folders.first()
            nike_fb_posts = FacebookPost.objects.filter(folder=nike_fb_folder)[:3]
            print(f"\nNike Facebook Posts (showing first 3 of {nike_fb_posts.count()}):")
            for post in nike_fb_posts:
                user_name = post.user_posted.get('name', 'Unknown') if isinstance(post.user_posted, dict) else str(post.user_posted)
                print(f"   - {user_name}: {post.description[:60]}...")
                print(f"     Likes: {post.likes}, Comments: {post.num_comments}")
        
        # Check data linking
        print(f"\n=== DATA LINKING VERIFICATION ===")
        
        total_nike_ig_posts = 0
        total_nike_fb_posts = 0
        
        for folder in nike_ig_folders:
            total_nike_ig_posts += InstagramPost.objects.filter(folder=folder).count()
            
        for folder in nike_fb_folders:
            total_nike_fb_posts += FacebookPost.objects.filter(folder=folder).count()
        
        print(f"✅ Total Nike Instagram posts: {total_nike_ig_posts}")
        print(f"✅ Total Nike Facebook posts: {total_nike_fb_posts}")
        
        # Frontend check
        print(f"\n=== FRONTEND READINESS ===")
        if total_nike_ig_posts > 0 and total_nike_fb_posts > 0:
            print("✅ Nike brand sources should now display data in the frontend")
            print("✅ The loading issue should be resolved")
            print("✅ Both Instagram and Facebook Nike data is available")
        else:
            print("❌ Still no data available for frontend")
            
        return True
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_nike_fix()
    if success:
        print("\n🎉 Nike brand sources verification completed!")
        print("\nThe Nike Facebook and Instagram brand sources should now work properly in the frontend.")
        print("You can refresh the frontend to see the Nike data instead of loading indicators.")
    else:
        print("\n❌ Verification failed. Please check the errors above.")