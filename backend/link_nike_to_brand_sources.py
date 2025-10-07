#!/usr/bin/env python
"""
Link Nike Apify Data to Brand Sources Folder

This script links the actual Nike data scraped from Apify actors to the 
Brand Sources folder so it displays the real Nike data.
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

def link_nike_data_to_brand_sources():
    """Link Nike Apify data to Brand Sources folder"""
    from track_accounts.models import UnifiedRunFolder
    from instagram_data.models import Folder as InstagramFolder, InstagramPost
    from facebook_data.models import Folder as FacebookFolder, FacebookPost
    from apify_integration.models import ApifyScraperRequest
    
    print("=== LINKING NIKE APIFY DATA TO BRAND SOURCES ===")
    
    try:
        # Get the Brand Sources folder
        brand_sources = UnifiedRunFolder.objects.filter(name__contains='Brand Sources').first()
        if not brand_sources:
            print("❌ Brand Sources folder not found")
            return False
            
        print(f"✅ Found Brand Sources folder: {brand_sources.name}")
        
        # Get Nike Apify requests
        nike_ig_request = ApifyScraperRequest.objects.filter(
            target_url__icontains='instagram.com/nike'
        ).first()
        
        nike_fb_request = ApifyScraperRequest.objects.filter(
            target_url__icontains='facebook.com/nike'
        ).first()
        
        if not nike_ig_request or not nike_fb_request:
            print("❌ Nike Apify requests not found")
            return False
            
        print(f"✅ Found Nike Instagram request: {nike_ig_request.request_id}")
        print(f"✅ Found Nike Facebook request: {nike_fb_request.request_id}")
        
        # Create or get Nike Instagram platform folder for Brand Sources
        nike_brand_ig_folder, ig_created = InstagramFolder.objects.get_or_create(
            unified_job_folder=brand_sources,
            name__icontains='Nike',
            defaults={
                'name': 'Nike Instagram - Brand Sources',
                'category': 'posts',
                'folder_type': 'content',
            }
        )
        
        if ig_created:
            print(f"✅ Created Nike Instagram folder for Brand Sources: {nike_brand_ig_folder.name}")
        else:
            print(f"✅ Found existing Nike Instagram folder: {nike_brand_ig_folder.name}")
        
        # Create or get Nike Facebook platform folder for Brand Sources  
        nike_brand_fb_folder, fb_created = FacebookFolder.objects.get_or_create(
            unified_job_folder=brand_sources,
            name__icontains='Nike',
            defaults={
                'name': 'Nike Facebook - Brand Sources',
                'category': 'posts',
                'folder_type': 'content',
            }
        )
        
        if fb_created:
            print(f"✅ Created Nike Facebook folder for Brand Sources: {nike_brand_fb_folder.name}")
        else:
            print(f"✅ Found existing Nike Facebook folder: {nike_brand_fb_folder.name}")
        
        # Link Nike Instagram posts to Brand Sources folder
        nike_ig_posts = InstagramPost.objects.filter(user_posted='nike')
        print(f"\n=== LINKING INSTAGRAM POSTS ===")
        print(f"Found {nike_ig_posts.count()} Nike Instagram posts")
        
        linked_ig_count = 0
        for post in nike_ig_posts:
            # Only link posts that aren't already linked to this folder
            if post.folder != nike_brand_ig_folder:
                post.folder = nike_brand_ig_folder
                post.save()
                linked_ig_count += 1
        
        print(f"✅ Linked {linked_ig_count} Instagram posts to Brand Sources")
        
        # Link Nike Facebook posts to Brand Sources folder
        nike_fb_posts = FacebookPost.objects.filter(
            user_posted__icontains='nike'
        )
        
        # Also check for posts where user_posted is a dict with Nike
        if nike_fb_posts.count() == 0:
            # Look for posts where user_posted contains Nike in the name
            all_fb_posts = FacebookPost.objects.all()
            nike_fb_posts = []
            for post in all_fb_posts:
                if isinstance(post.user_posted, dict):
                    user_name = post.user_posted.get('name', '').lower()
                    if 'nike' in user_name:
                        nike_fb_posts.append(post)
                elif 'nike' in str(post.user_posted).lower():
                    nike_fb_posts.append(post)
        
        print(f"\n=== LINKING FACEBOOK POSTS ===")
        print(f"Found {len(nike_fb_posts)} Nike Facebook posts")
        
        linked_fb_count = 0
        for post in nike_fb_posts:
            # Only link posts that aren't already linked to this folder
            if post.folder != nike_brand_fb_folder:
                post.folder = nike_brand_fb_folder
                post.save()
                linked_fb_count += 1
        
        print(f"✅ Linked {linked_fb_count} Facebook posts to Brand Sources")
        
        # Verify the linking
        print(f"\n=== VERIFICATION ===")
        final_ig_count = InstagramPost.objects.filter(folder=nike_brand_ig_folder).count()
        final_fb_count = FacebookPost.objects.filter(folder=nike_brand_fb_folder).count()
        
        print(f"✅ Brand Sources Instagram folder now has: {final_ig_count} posts")
        print(f"✅ Brand Sources Facebook folder now has: {final_fb_count} posts")
        
        # Show sample data
        if final_ig_count > 0:
            print(f"\nSample Instagram posts in Brand Sources:")
            sample_ig = InstagramPost.objects.filter(folder=nike_brand_ig_folder)[:3]
            for post in sample_ig:
                print(f"  - {post.user_posted}: {post.description[:60]}...")
                print(f"    Likes: {post.likes}, Comments: {post.num_comments}")
        
        if final_fb_count > 0:
            print(f"\nSample Facebook posts in Brand Sources:")
            sample_fb = FacebookPost.objects.filter(folder=nike_brand_fb_folder)[:3]
            for post in sample_fb:
                user_name = post.user_posted.get('name', 'Unknown') if isinstance(post.user_posted, dict) else str(post.user_posted)
                print(f"  - {user_name}: {post.description[:60]}...")
                print(f"    Likes: {post.likes}, Comments: {post.num_comments}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error linking Nike data to Brand Sources: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = link_nike_data_to_brand_sources()
    if success:
        print("\n🎉 Nike Apify data successfully linked to Brand Sources!")
        print("\nThe Brand Sources folder should now show:")
        print("- Instagram: Real Nike data from Apify actor nH2AHrwxeTRJoN5hX")
        print("- Facebook: Real Nike data from Apify actor KoJrdxJCTtpon81KY")
        print("\nRefresh your frontend to see the Nike data in Brand Sources.")
    else:
        print("\n❌ Failed to link Nike data. Please check the errors above.")