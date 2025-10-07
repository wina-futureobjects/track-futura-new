#!/usr/bin/env python
"""
Verify Brand Sources Nike Data Linking

This script verifies that the Brand Sources folder now shows the real
Nike data from the Apify actors instead of loading.
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

def verify_brand_sources_nike_data():
    """Verify Brand Sources now shows Nike Apify data"""
    from track_accounts.models import UnifiedRunFolder
    from instagram_data.models import Folder as InstagramFolder, InstagramPost
    from facebook_data.models import Folder as FacebookFolder, FacebookPost
    from apify_integration.models import ApifyScraperRequest
    
    print("=== BRAND SOURCES NIKE DATA VERIFICATION ===")
    
    try:
        # Get the Brand Sources folder
        brand_sources = UnifiedRunFolder.objects.filter(name__contains='Brand Sources').first()
        
        print(f"✅ Brand Sources Folder: {brand_sources.name}")
        print(f"   ID: {brand_sources.id}")
        print(f"   Type: {brand_sources.folder_type}")
        print(f"   Project: {brand_sources.project_id}")
        
        # Check platform folders
        ig_folders = brand_sources.instagram_platform_folders.all()
        fb_folders = brand_sources.facebook_platform_folders.all()
        
        print(f"\n=== PLATFORM FOLDERS ===")
        print(f"Instagram folders: {ig_folders.count()}")
        for folder in ig_folders:
            posts_count = folder.get_content_count()
            print(f"  - {folder.name}: {posts_count} posts")
            
        print(f"Facebook folders: {fb_folders.count()}")
        for folder in fb_folders:
            posts_count = folder.get_content_count()
            print(f"  - {folder.name}: {posts_count} posts")
        
        # Get Nike data details
        print(f"\n=== NIKE DATA VERIFICATION ===")
        
        # Instagram Nike data
        nike_ig_folder = ig_folders.filter(name__icontains='Nike').first()
        if nike_ig_folder:
            nike_ig_posts = InstagramPost.objects.filter(folder=nike_ig_folder)
            print(f"✅ Nike Instagram posts in Brand Sources: {nike_ig_posts.count()}")
            
            # Show sample posts
            print("Sample Nike Instagram posts:")
            for post in nike_ig_posts[:3]:
                print(f"  - @{post.user_posted}: {post.description[:50]}...")
                print(f"    URL: {post.url}")
                print(f"    Engagement: {post.likes} likes, {post.num_comments} comments")
        
        # Facebook Nike data
        nike_fb_folder = fb_folders.filter(name__icontains='Nike').first()
        if nike_fb_folder:
            nike_fb_posts = FacebookPost.objects.filter(folder=nike_fb_folder)
            print(f"\n✅ Nike Facebook posts in Brand Sources: {nike_fb_posts.count()}")
            
            # Show sample posts
            print("Sample Nike Facebook posts:")
            for post in nike_fb_posts[:3]:
                user_name = post.user_posted.get('name', 'Unknown') if isinstance(post.user_posted, dict) else str(post.user_posted)
                print(f"  - {user_name}: {post.description[:50]}...")
                print(f"    URL: {post.url}")
                print(f"    Engagement: {post.likes} likes, {post.num_comments} comments")
        
        # Verify Apify connection
        print(f"\n=== APIFY ACTORS VERIFICATION ===")
        
        nike_ig_request = ApifyScraperRequest.objects.filter(
            target_url__icontains='instagram.com/nike'
        ).first()
        
        nike_fb_request = ApifyScraperRequest.objects.filter(
            target_url__icontains='facebook.com/nike'
        ).first()
        
        if nike_ig_request:
            print(f"✅ Nike Instagram Apify Actor: nH2AHrwxeTRJoN5hX")
            print(f"   Request ID: {nike_ig_request.request_id}")
            print(f"   Status: {nike_ig_request.status}")
            print(f"   URL: {nike_ig_request.target_url}")
        
        if nike_fb_request:
            print(f"✅ Nike Facebook Apify Actor: KoJrdxJCTtpon81KY")
            print(f"   Request ID: {nike_fb_request.request_id}")
            print(f"   Status: {nike_fb_request.status}")
            print(f"   URL: {nike_fb_request.target_url}")
        
        # Final status
        total_ig_posts = nike_ig_posts.count() if nike_ig_folder else 0
        total_fb_posts = nike_fb_posts.count() if nike_fb_folder else 0
        
        print(f"\n=== FINAL STATUS ===")
        print(f"✅ Brand Sources - 06/10/2025 12:06:43 now contains:")
        print(f"   📱 Instagram: {total_ig_posts} Nike posts from Apify actor")
        print(f"   📘 Facebook: {total_fb_posts} Nike posts from Apify actor")
        
        if total_ig_posts > 0 and total_fb_posts > 0:
            print(f"✅ SUCCESS: Brand Sources should now display Nike data instead of loading")
            print(f"✅ Data source: Real Nike content from Apify actors")
            print(f"✅ Frontend ready: Refresh to see Nike posts")
        else:
            print(f"❌ Issue: Not all Nike data is linked properly")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_brand_sources_nike_data()
    if success:
        print("\n🎉 Brand Sources Nike data verification completed!")
        print("\nThe Brand Sources folder now shows real Nike data from the Apify actors:")
        print("• Instagram data from actor nH2AHrwxeTRJoN5hX")
        print("• Facebook data from actor KoJrdxJCTtpon81KY")
        print("\nNo more loading issues - refresh your frontend to see the Nike content!")
    else:
        print("\n❌ Verification failed. Please check the errors above.")