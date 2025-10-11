#!/usr/bin/env python3
"""
SIMPLE PRODUCTION TEST SCRIPT
============================
Quick test to see what's in production database
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def test_production_database():
    print("TESTING PRODUCTION DATABASE")
    print("=" * 50)
    
    try:
        from brightdata_integration.models import BrightDataScrapedPost
        from track_accounts.models import UnifiedRunFolder
        from django.db import connection
        
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("Database connection: WORKING")
        
        # Check scraped posts
        post_count = BrightDataScrapedPost.objects.count()
        print(f"BrightDataScrapedPost records: {post_count}")
        
        if post_count > 0:
            recent_posts = BrightDataScrapedPost.objects.all()[:5]
            for post in recent_posts:
                print(f"   Post ID: {post.id}, Platform: {post.platform}, Folder: {post.folder_id}")
        
        # Check job folders
        job_folders = UnifiedRunFolder.objects.filter(folder_type='job')
        print(f"Job folders: {job_folders.count()}")
        
        for folder in job_folders[:5]:
            linked_posts = BrightDataScrapedPost.objects.filter(folder_id=folder.id).count()
            print(f"   Folder {folder.name} (ID: {folder.id}): {linked_posts} posts")
        
        # Check specific folders 103 and 104
        for folder_id in [103, 104]:
            try:
                folder = UnifiedRunFolder.objects.get(id=folder_id)
                posts = BrightDataScrapedPost.objects.filter(folder_id=folder_id).count()
                print(f"Folder {folder_id} ({folder.name}): {posts} posts")
            except UnifiedRunFolder.DoesNotExist:
                print(f"Folder {folder_id}: NOT FOUND")
        
        print("\nIf you have data, it should be at:")
        print("   Job 2: /organizations/1/projects/1/data-storage/job/103")
        print("   Job 3: /organizations/1/projects/1/data-storage/job/104")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_production_database()
