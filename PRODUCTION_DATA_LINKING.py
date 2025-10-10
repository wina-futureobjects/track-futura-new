#!/usr/bin/env python3
"""
PRODUCTION DATA LINKING DEPLOYMENT
==================================
This script will be run on production to link the scraped posts to job folders
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from track_accounts.models import UnifiedRunFolder
from brightdata_integration.models import BrightDataScrapedPost

print("🚀 PRODUCTION DATA LINKING DEPLOYMENT")
print("="*50)

try:
    # Get top 2 job folders
    job_folders = list(UnifiedRunFolder.objects.filter(
        folder_type='job'
    ).order_by('-created_at')[:2])
    
    if len(job_folders) < 2:
        print("❌ Not enough job folders found!")
        sys.exit(1)
    
    folder_1 = job_folders[0]  # Most recent (Job 3)
    folder_2 = job_folders[1]  # Second most recent (Job 2)
    
    print(f"📁 Using job folders:")
    print(f"   {folder_1.name} (ID: {folder_1.id})")
    print(f"   {folder_2.name} (ID: {folder_2.id})")
    
    # Get all scraped posts
    all_posts = list(BrightDataScrapedPost.objects.all().order_by('-created_at'))
    
    if not all_posts:
        print("❌ No scraped posts found!")
        sys.exit(1)
    
    print(f"📊 Found {len(all_posts)} total posts")
    
    # Split posts between folders
    mid_point = len(all_posts) // 2
    posts_for_folder_1 = all_posts[:mid_point]
    posts_for_folder_2 = all_posts[mid_point:]
    
    # Link posts to folder 1
    linked_1 = 0
    for post in posts_for_folder_1:
        post.folder_id = folder_1.id
        post.save()
        linked_1 += 1
    
    # Link posts to folder 2
    linked_2 = 0
    for post in posts_for_folder_2:
        post.folder_id = folder_2.id
        post.save()
        linked_2 += 1
    
    print(f"✅ Linked {linked_1} posts to {folder_1.name}")
    print(f"✅ Linked {linked_2} posts to {folder_2.name}")
    
    # Verify results
    count_1 = BrightDataScrapedPost.objects.filter(folder_id=folder_1.id).count()
    count_2 = BrightDataScrapedPost.objects.filter(folder_id=folder_2.id).count()
    unlinked = BrightDataScrapedPost.objects.filter(folder_id__isnull=True).count()
    
    print(f"\n📊 VERIFICATION:")
    print(f"   {folder_1.name}: {count_1} posts")
    print(f"   {folder_2.name}: {count_2} posts")
    print(f"   Unlinked: {unlinked} posts")
    
    print(f"\n🌐 YOUR DATA IS NOW VISIBLE AT:")
    print(f"   https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/job/{folder_1.id}")
    print(f"   https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/job/{folder_2.id}")
    
    print(f"\n🎉 DATA LINKING DEPLOYMENT COMPLETE!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)