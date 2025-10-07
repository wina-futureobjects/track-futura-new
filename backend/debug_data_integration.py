#!/usr/bin/env python
"""
DEBUG DATA INTEGRATION SERVICE

This script will debug exactly why DataIntegrationService is not finding Nike posts
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

def debug_data_integration():
    """Debug the DataIntegrationService step by step"""
    from track_accounts.models import SourceFolder, TrackSource, UnifiedRunFolder
    from instagram_data.models import Folder as InstagramFolder, InstagramPost
    from facebook_data.models import Folder as FacebookFolder, FacebookPost
    from common.data_integration_service import DataIntegrationService
    from datetime import datetime, timedelta
    from django.utils import timezone
    
    print("=== DEBUGGING DATA INTEGRATION SERVICE ===")
    
    try:
        # Simulate exactly what the service does
        project_id = 6
        
        print(f"Step 1: Testing source folder mapping...")
        data_service = DataIntegrationService(project_id=project_id)
        mapping = data_service._get_source_folder_mapping()
        
        print(f"Found {len(mapping)} sources in mapping:")
        for source_id, info in mapping.items():
            print(f"  Source {source_id}: {info}")
        
        print(f"\nStep 2: Testing manual folder filtering...")
        
        # Test Instagram folders for project 6
        ig_folders = InstagramFolder.objects.filter(project_id=project_id)
        print(f"Instagram folders for project {project_id}: {ig_folders.count()}")
        
        for folder in ig_folders:
            posts = InstagramPost.objects.filter(folder=folder)
            print(f"  - {folder.name}: {posts.count()} posts (project: {folder.project_id})")
        
        # Test Facebook folders for project 6
        fb_folders = FacebookFolder.objects.filter(project_id=project_id)
        print(f"Facebook folders for project {project_id}: {fb_folders.count()}")
        
        for folder in fb_folders:
            posts = FacebookPost.objects.filter(folder=folder)
            print(f"  - {folder.name}: {posts.count()} posts (project: {folder.project_id})")
        
        print(f"\nStep 3: Testing manual post filtering...")
        
        # Test getting posts with date filter
        cutoff_date = timezone.now() - timedelta(days=90)
        print(f"Cutoff date: {cutoff_date}")
        
        ig_posts = InstagramPost.objects.filter(
            folder__in=ig_folders,
            created_at__gte=cutoff_date
        )
        print(f"Instagram posts after cutoff: {ig_posts.count()}")
        
        fb_posts = FacebookPost.objects.filter(
            folder__in=fb_folders,
            created_at__gte=cutoff_date
        )
        print(f"Facebook posts after cutoff: {fb_posts.count()}")
        
        print(f"\nStep 4: Testing username matching manually...")
        
        # Get Nike sources
        nike_sources = TrackSource.objects.filter(
            project_id=project_id,
            name__icontains='nike'
        )
        
        print(f"Nike sources: {nike_sources.count()}")
        
        for source in nike_sources:
            print(f"  Source: {source.name}")
            print(f"    Instagram: {source.instagram_link}")
            print(f"    Facebook: {source.facebook_link}")
            print(f"    Folder: {source.folder.name if source.folder else 'None'}")
            print(f"    Folder type: {source.folder.folder_type if source.folder else 'None'}")
        
        # Test manual matching
        print(f"\nStep 5: Manual username matching test...")
        
        def test_manual_matching(username, platform):
            print(f"  Testing username '{username}' for {platform}:")
            
            sources = TrackSource.objects.filter(project_id=project_id)
            for source in sources:
                source_url = None
                if platform == 'instagram' and source.instagram_link:
                    source_url = source.instagram_link
                elif platform == 'facebook' and source.facebook_link:
                    source_url = source.facebook_link
                
                if source_url and username and username.lower() in source_url.lower():
                    print(f"    MATCH: {source.name} -> {source_url}")
                    if source.folder:
                        print(f"           Folder: {source.folder.name} ({source.folder.folder_type})")
                        return source.folder.folder_type, source.folder.name
                    else:
                        print(f"           NO FOLDER!")
            
            print(f"    NO MATCH for '{username}'")
            return 'unknown', None
        
        # Test with Nike usernames
        test_manual_matching('nike', 'instagram')
        test_manual_matching('nike', 'facebook')
        
        print(f"\nStep 6: Test actual posts...")
        
        # Get some actual Nike posts
        nike_ig_posts = InstagramPost.objects.filter(
            folder__in=ig_folders,
            user_posted='nike'
        )[:3]
        
        print(f"Sample Nike Instagram posts:")
        for post in nike_ig_posts:
            print(f"  - User: '{post.user_posted}'")
            print(f"    Folder: {post.folder.name}")
            print(f"    Created: {post.created_at}")
            
            # Test matching for this post
            result = test_manual_matching(post.user_posted, 'instagram')
            print(f"    Match result: {result}")
        
        print(f"\nStep 7: Call DataIntegrationService directly...")
        
        # Test the actual service call
        company_posts = data_service.get_all_posts(
            limit=10,
            days_back=90,
            platform='instagram',
            source_type='company'
        )
        
        print(f"DataIntegrationService returned: {len(company_posts)} company posts")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during debug: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_data_integration()