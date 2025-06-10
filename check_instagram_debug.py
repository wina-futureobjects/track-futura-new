#!/usr/bin/env python3
"""
Simple Instagram Webhook Debug Checker
This script checks your existing Instagram folders and scraper requests
"""

import os
import sys
import django
import json

# Setup Django
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.chdir(backend_path)
django.setup()

from brightdata_integration.models import ScraperRequest
from instagram_data.models import InstagramPost, Folder

def main():
    print("🔍 Instagram Webhook Debug Check")
    print("=" * 50)

    # Check Instagram folders
    print("\n📁 Instagram Folders:")
    folders = Folder.objects.all().order_by('-created_at')
    for folder in folders:
        post_count = InstagramPost.objects.filter(folder=folder).count()
        print(f"  - {folder.name} (ID: {folder.id}) - {post_count} posts")

        if post_count > 0:
            recent_posts = InstagramPost.objects.filter(folder=folder).order_by('-id')[:3]
            for post in recent_posts:
                print(f"    * Post ID: {post.post_id} - {post.description[:50] if post.description else 'No description'}...")

    # Check recent scraper requests
    print(f"\n📋 Recent Scraper Requests:")
    recent_requests = ScraperRequest.objects.filter(platform='instagram').order_by('-created_at')[:10]
    for req in recent_requests:
        print(f"  - Request ID: {req.request_id}")
        print(f"    Status: {req.status}")
        print(f"    Folder ID: {req.folder_id}")
        print(f"    Created: {req.created_at}")
        print()

    # Check posts without folders
    print(f"\n🔍 Instagram Posts without Folders:")
    orphan_posts = InstagramPost.objects.filter(folder__isnull=True).order_by('-id')[:5]
    for post in orphan_posts:
        print(f"  - Post ID: {post.post_id} - {post.description[:50] if post.description else 'No description'}...")

    # Summary
    total_folders = folders.count()
    total_posts = InstagramPost.objects.count()
    posts_with_folders = InstagramPost.objects.filter(folder__isnull=False).count()

    print(f"\n📊 Summary:")
    print(f"  Total Instagram folders: {total_folders}")
    print(f"  Total Instagram posts: {total_posts}")
    print(f"  Posts with folders: {posts_with_folders}")
    print(f"  Posts without folders: {total_posts - posts_with_folders}")

if __name__ == "__main__":
    main()
