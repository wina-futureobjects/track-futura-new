#!/usr/bin/env python
"""
Check UnifiedRunFolder table to find the actual Nike data
"""

import os
import sys
import django

# Add backend directory to Python path
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from track_accounts.models import UnifiedRunFolder
from brightdata_integration.models import BrightDataScrapedPost

def check_unified_run_folders():
    print("🔍 CHECKING UNIFIEDRUNFOLDER TABLE")
    print("=" * 50)
    
    folders = UnifiedRunFolder.objects.all()
    print(f"📊 Total UnifiedRunFolders: {folders.count()}")
    
    for folder in folders:
        print(f"\n📂 Folder ID {folder.id}: {folder.name}")
        print(f"   Project ID: {folder.project_id}")
        print(f"   Created: {folder.created_at}")
        print(f"   Updated: {folder.updated_at}")
        
        # Check for subfolders
        ig_folders = folder.instagram_platform_folders.all()
        fb_folders = folder.facebook_platform_folders.all()
        
        print(f"   Instagram subfolders: {ig_folders.count()}")
        for ig_folder in ig_folders:
            print(f"     📸 IG Folder {ig_folder.id}: {getattr(ig_folder, 'name', 'unnamed')}")
            
        print(f"   Facebook subfolders: {fb_folders.count()}")
        for fb_folder in fb_folders:
            print(f"     📘 FB Folder {fb_folder.id}: {getattr(fb_folder, 'name', 'unnamed')}")
            
        # Check for posts (simplified)
        print(f"   Has posts: checking...")

if __name__ == "__main__":
    check_unified_run_folders()