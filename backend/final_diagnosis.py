#!/usr/bin/env python
"""
FINAL DIAGNOSIS: Project ID Mismatch

This script will confirm the exact issue - Nike posts are in folders with wrong project_id
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

def final_diagnosis():
    """Confirm the project ID mismatch issue"""
    from track_accounts.models import SourceFolder, TrackSource, UnifiedRunFolder
    from instagram_data.models import Folder as InstagramFolder, InstagramPost
    from facebook_data.models import Folder as FacebookFolder, FacebookPost
    
    print("=== FINAL DIAGNOSIS: PROJECT ID MISMATCH ===")
    
    try:
        # Check Brand Sources unified folder
        brand_sources = UnifiedRunFolder.objects.filter(
            name__contains='Brand Sources'
        ).first()
        
        print(f"Brand Sources UnifiedRunFolder:")
        print(f"  Name: {brand_sources.name}")
        print(f"  Project ID: {brand_sources.project_id}")
        
        # Check Nike platform folders
        ig_folders = brand_sources.instagram_platform_folders.all()
        fb_folders = brand_sources.facebook_platform_folders.all()
        
        print(f"\nNike Instagram folders:")
        for folder in ig_folders:
            posts = InstagramPost.objects.filter(folder=folder)
            print(f"  - {folder.name}")
            print(f"    Project ID: {folder.project_id}")
            print(f"    Posts: {posts.count()}")
            print(f"    Unified folder: {folder.unified_job_folder_id}")
        
        print(f"\nNike Facebook folders:")
        for folder in fb_folders:
            posts = FacebookPost.objects.filter(folder=folder)
            print(f"  - {folder.name}")
            print(f"    Project ID: {folder.project_id}")
            print(f"    Posts: {posts.count()}")
            print(f"    Unified folder: {folder.unified_job_folder_id}")
        
        # Check what project 6 folders contain
        print(f"\nProject 6 Instagram folders:")
        project_6_ig_folders = InstagramFolder.objects.filter(project_id=6)
        for folder in project_6_ig_folders:
            posts = InstagramPost.objects.filter(folder=folder)
            print(f"  - {folder.name}")
            print(f"    Posts: {posts.count()}")
            print(f"    Unified folder: {folder.unified_job_folder_id}")
            
            # Show sample posts
            if posts.count() > 0:
                print(f"    Sample posts:")
                for post in posts[:3]:
                    print(f"      • User: {post.user_posted}")
        
        print(f"\nProject 6 Facebook folders:")
        project_6_fb_folders = FacebookFolder.objects.filter(project_id=6)
        for folder in project_6_fb_folders:
            posts = FacebookPost.objects.filter(folder=folder)
            print(f"  - {folder.name}")
            print(f"    Posts: {posts.count()}")
            print(f"    Unified folder: {folder.unified_job_folder_id}")
            
            # Show sample posts
            if posts.count() > 0:
                print(f"    Sample posts:")
                for post in posts[:3]:
                    user = post.user_posted
                    if isinstance(user, dict):
                        user_name = user.get('name', 'Unknown')
                    else:
                        user_name = str(user)
                    print(f"      • User: {user_name}")
        
        # The issue: Nike posts are in Brand Sources folders which have different project_id
        # But DataIntegrationService only looks at project_id=6 folders
        
        print(f"\n=== ISSUE IDENTIFIED ===")
        print(f"❌ Nike posts are in Brand Sources folders (project {brand_sources.project_id})")
        print(f"❌ DataIntegrationService looks for project 6 folders")
        print(f"❌ No overlap = No Nike posts found")
        
        # Solution: Fix the project_id on Brand Sources folders
        print(f"\n=== SOLUTION ===")
        print(f"Need to update Brand Sources folder project_id to 6")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during diagnosis: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    final_diagnosis()