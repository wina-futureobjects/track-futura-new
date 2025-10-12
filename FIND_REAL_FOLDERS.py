#!/usr/bin/env python3
"""
Find the actual run folders and their data
"""

import os
import sys
import django

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.append(backend_path)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from brightdata_integration.models import BrightDataScrapedPost, BrightDataScraperRequest
from track_accounts.models import UnifiedRunFolder

def find_all_run_folders():
    """Find all run folders and their data"""
    
    print("🔍 FINDING ALL RUN FOLDERS")
    print("=" * 60)
    
    # Get all run folders
    run_folders = UnifiedRunFolder.objects.filter(folder_type='run').order_by('-id')
    
    print(f"Found {run_folders.count()} run folders:")
    print("")
    
    for folder in run_folders[:10]:  # Show latest 10
        post_count = BrightDataScrapedPost.objects.filter(folder_id=folder.id).count()
        request_count = BrightDataScraperRequest.objects.filter(folder_id=folder.id).count()
        
        print(f"📁 ID {folder.id}: '{folder.name}'")
        print(f"   Created: {folder.created_at}")
        print(f"   Posts: {post_count}, Requests: {request_count}")
        
        if post_count > 0:
            sample_post = BrightDataScrapedPost.objects.filter(folder_id=folder.id).first()
            print(f"   Sample: {sample_post.platform} post by {sample_post.user_posted}")
            
        print(f"   🌐 Current URL: /organizations/1/projects/1/data-storage/run/{folder.id}")
        print(f"   🌐 Future URL: /organizations/1/projects/1/data-storage/{folder.name.replace(' ', '%20')}/1")
        print("")

def check_folder_271_issue():
    """Check why folder 271 doesn't exist"""
    
    print("🔍 CHECKING FOLDER 271 ISSUE")
    print("=" * 60)
    
    # Check if folder 271 exists in any form
    all_folders = UnifiedRunFolder.objects.filter(id=271)
    if all_folders.exists():
        folder = all_folders.first()
        print(f"✅ Found folder 271: '{folder.name}' (type: {folder.folder_type})")
    else:
        print("❌ Folder 271 does not exist in database")
    
    # Check the highest ID folder
    highest_folder = UnifiedRunFolder.objects.order_by('-id').first()
    if highest_folder:
        print(f"🔝 Highest ID folder: {highest_folder.id} - '{highest_folder.name}'")
    
    # Check if there are any folders with posts that might be your latest data
    folders_with_posts = BrightDataScrapedPost.objects.values_list('folder_id', flat=True).distinct()
    print(f"\n📊 Folders with scraped posts: {list(folders_with_posts)}")

if __name__ == "__main__":
    find_all_run_folders()
    check_folder_271_issue()
    
    print("🎯 The URL /data-storage/run/271 suggests frontend is creating")
    print("   non-existent folder IDs. Let's check what's really happening...")