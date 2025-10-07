#!/usr/bin/env python
"""
Nike Data Investigation Script

This script investigates why Nike brand sources are showing as loading
instead of displaying the scraped data.
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

def investigate_nike_data():
    """Investigate Nike data in the system"""
    print("=== NIKE DATA INVESTIGATION ===")
    print()
    
    try:
        from instagram_data.models import InstagramPost, Folder as InstagramFolder
        from facebook_data.models import FacebookPost, Folder as FacebookFolder
        from track_accounts.models import UnifiedRunFolder
        
        # Check Instagram data for Nike
        print("=== INSTAGRAM DATA ===")
        ig_posts = InstagramPost.objects.all().order_by('-created_at')[:10]
        print(f"Total Instagram posts: {InstagramPost.objects.count()}")
        
        for i, post in enumerate(ig_posts, 1):
            desc = post.description[:50] if post.description else "No description"
            folder_name = post.folder.name if post.folder else "No folder"
            print(f"{i}. User: {post.user_posted}")
            print(f"   Description: {desc}...")
            print(f"   Folder: {folder_name}")
            print(f"   URL: {post.url}")
            print(f"   Likes: {post.likes}, Comments: {post.num_comments}")
            print()
        
        # Check Instagram folders
        print("=== INSTAGRAM FOLDERS ===")
        ig_folders = InstagramFolder.objects.all().order_by('-created_at')
        for folder in ig_folders:
            posts_count = folder.get_content_count()
            print(f"- {folder.name}: {posts_count} posts")
            print(f"  Type: {folder.folder_type}, Category: {folder.category}")
            print(f"  Created: {folder.created_at}")
            if folder.unified_job_folder:
                print(f"  Unified folder: {folder.unified_job_folder.name}")
            print()
        
        # Check Facebook data
        print("=== FACEBOOK DATA ===")
        fb_posts = FacebookPost.objects.all().order_by('-created_at')[:10]
        print(f"Total Facebook posts: {FacebookPost.objects.count()}")
        
        for i, post in enumerate(fb_posts, 1):
            desc = post.description[:50] if post.description else "No description"
            folder_name = post.folder.name if post.folder else "No folder"
            print(f"{i}. User: {post.user_posted}")
            print(f"   Description: {desc}...")
            print(f"   Folder: {folder_name}")
            print(f"   URL: {post.url}")
            print(f"   Likes: {post.likes}, Comments: {post.num_comments}")
            print()
        
        # Check Facebook folders
        print("=== FACEBOOK FOLDERS ===")
        fb_folders = FacebookFolder.objects.all().order_by('-created_at')
        for folder in fb_folders:
            posts_count = folder.get_content_count()
            print(f"- {folder.name}: {posts_count} posts")
            print(f"  Type: {folder.folder_type}, Category: {folder.category}")
            print(f"  Created: {folder.created_at}")
            if folder.unified_job_folder:
                print(f"  Unified folder: {folder.unified_job_folder.name}")
            print()
        
        # Check unified folders
        print("=== UNIFIED FOLDERS ===")
        unified_folders = UnifiedRunFolder.objects.all().order_by('-created_at')[:5]
        for folder in unified_folders:
            print(f"- {folder.name}")
            print(f"  Type: {folder.folder_type}")
            print(f"  Created: {folder.created_at}")
            
            # Check if this folder has platform folders
            ig_platform_folders = folder.instagram_platform_folders.all()
            fb_platform_folders = folder.facebook_platform_folders.all()
            
            print(f"  Instagram platform folders: {ig_platform_folders.count()}")
            print(f"  Facebook platform folders: {fb_platform_folders.count()}")
            print()
        
        # Check for Nike-specific data
        print("=== NIKE-SPECIFIC SEARCH ===")
        nike_ig_posts = InstagramPost.objects.filter(user_posted__icontains='nike')
        nike_fb_posts = FacebookPost.objects.filter(user_posted__icontains='nike')
        
        print(f"Instagram posts mentioning 'nike': {nike_ig_posts.count()}")
        print(f"Facebook posts mentioning 'nike': {nike_fb_posts.count()}")
        
        # Also check descriptions
        nike_ig_desc = InstagramPost.objects.filter(description__icontains='nike')
        nike_fb_desc = FacebookPost.objects.filter(description__icontains='nike')
        
        print(f"Instagram posts with 'nike' in description: {nike_ig_desc.count()}")
        print(f"Facebook posts with 'nike' in description: {nike_fb_desc.count()}")
        
    except Exception as e:
        print(f"Error during investigation: {e}")
        import traceback
        traceback.print_exc()

def check_frontend_api():
    """Check what API endpoints might be used for displaying Nike data"""
    print("=== API ENDPOINT INVESTIGATION ===")
    print()
    
    try:
        # Check if there are any API views that might be serving this data
        from django.urls import get_resolver
        from django.conf import settings
        
        print("Checking for API endpoints that might serve brand source data...")
        
        # Look for views that might handle brand sources or Nike data
        import track_accounts.views as track_views
        
        # Check if there are specific functions for handling brand data
        view_functions = [func for func in dir(track_views) if not func.startswith('_')]
        print("Available view functions in track_accounts:")
        for func in view_functions:
            if 'brand' in func.lower() or 'source' in func.lower() or 'nike' in func.lower():
                print(f"  - {func} (potential brand-related)")
            elif func.endswith('view') or func.endswith('list'):
                print(f"  - {func}")
        
    except Exception as e:
        print(f"Error checking API endpoints: {e}")

if __name__ == "__main__":
    investigate_nike_data()
    check_frontend_api()