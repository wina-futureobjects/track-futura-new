#!/usr/bin/env python3
"""
Detailed Folder Debug - Check specific folder and scraper requests
"""

import os
import sys
import django

# Setup Django
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.chdir(backend_path)
django.setup()

from brightdata_integration.models import ScraperRequest
from instagram_data.models import InstagramPost, Folder

def main():
    print("🔍 Detailed Instagram Folder Debug")
    print("=" * 60)

    # Get the newest folder
    newest_folder = Folder.objects.order_by('-created_at').first()
    if newest_folder:
        print(f"\n📁 Newest Folder: {newest_folder.name} (ID: {newest_folder.id})")
        print(f"   Created: {newest_folder.created_at}")
        print(f"   Description: {newest_folder.description}")

        # Check posts in this folder
        posts_count = InstagramPost.objects.filter(folder=newest_folder).count()
        print(f"   Posts count: {posts_count}")

        # Check scraper requests for this folder
        print(f"\n📋 Scraper Requests for Folder ID {newest_folder.id}:")
        scraper_requests = ScraperRequest.objects.filter(
            platform='instagram',
            folder_id=newest_folder.id
        ).order_by('-created_at')

        for req in scraper_requests:
            print(f"   - Request ID: {req.request_id}")
            print(f"     Status: {req.status}")
            print(f"     Created: {req.created_at}")
            print(f"     Target URL: {req.target_url}")
            print(f"     Error: {req.error_message or 'None'}")
            print()

    # Check recent scraper requests (last 10)
    print(f"\n📋 Recent Instagram Scraper Requests:")
    recent_requests = ScraperRequest.objects.filter(platform='instagram').order_by('-created_at')[:10]

    for req in recent_requests:
        folder_name = "Unknown"
        try:
            if req.folder_id:
                folder = Folder.objects.get(id=req.folder_id)
                folder_name = folder.name
        except Folder.DoesNotExist:
            folder_name = f"Missing Folder (ID: {req.folder_id})"

        print(f"   - Request ID: {req.request_id}")
        print(f"     Status: {req.status}")
        print(f"     Folder: {folder_name} (ID: {req.folder_id})")
        print(f"     Created: {req.created_at}")
        print(f"     Error: {req.error_message or 'None'}")
        print()

    # Check if there are any orphaned posts (posts without folders that might belong to recent requests)
    print(f"\n🔍 Recent Posts Analysis:")
    all_recent_posts = InstagramPost.objects.order_by('-id')[:20]

    for post in all_recent_posts:
        folder_info = f"Folder: {post.folder.name} (ID: {post.folder.id})" if post.folder else "No Folder"
        print(f"   - Post ID: {post.post_id}")
        print(f"     {folder_info}")
        print(f"     Content: {(post.description or '')[:50]}...")
        print()

if __name__ == "__main__":
    main()
