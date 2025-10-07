#!/usr/bin/env python
"""
CHECK MISSING FOLDER IDS

Check which folder IDs are causing 404 errors
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

def check_missing_folders():
    """Check which folder IDs are missing and causing 404s"""
    from facebook_data.models import Folder as FacebookFolder
    from instagram_data.models import Folder as InstagramFolder
    from track_accounts.models import ReportFolder, UnifiedRunFolder
    
    print("=== CHECKING MISSING FOLDER IDS ===")
    
    # Check the problematic IDs from the error log
    problematic_ids = [11, 13, 21]
    
    for folder_id in problematic_ids:
        print(f"\nChecking ID {folder_id}:")
        
        # Check Facebook folders
        fb_folder = FacebookFolder.objects.filter(id=folder_id).first()
        if fb_folder:
            posts = fb_folder.posts.count()
            print(f"  ✅ Facebook folder: {fb_folder.name} ({posts} posts)")
        else:
            print(f"  ❌ No Facebook folder with ID {folder_id}")
        
        # Check Instagram folders
        ig_folder = InstagramFolder.objects.filter(id=folder_id).first()
        if ig_folder:
            posts = ig_folder.posts.count()
            print(f"  ✅ Instagram folder: {ig_folder.name} ({posts} posts)")
        else:
            print(f"  ❌ No Instagram folder with ID {folder_id}")
        
        # Check Report folders
        report_folder = ReportFolder.objects.filter(id=folder_id).first()
        if report_folder:
            print(f"  ✅ Report folder: {report_folder.name}")
        else:
            print(f"  ❌ No Report folder with ID {folder_id}")
        
        # Check Unified folders
        unified_folder = UnifiedRunFolder.objects.filter(id=folder_id).first()
        if unified_folder:
            print(f"  ✅ Unified folder: {unified_folder.name}")
        else:
            print(f"  ❌ No Unified folder with ID {folder_id}")
    
    # List all existing folder IDs
    print(f"\n=== ALL EXISTING FOLDER IDS ===")
    
    fb_folders = FacebookFolder.objects.all()
    print(f"Facebook folders: {[f.id for f in fb_folders]}")
    
    ig_folders = InstagramFolder.objects.all()
    print(f"Instagram folders: {[f.id for f in ig_folders]}")
    
    report_folders = ReportFolder.objects.all()
    print(f"Report folders: {[f.id for f in report_folders]}")
    
    unified_folders = UnifiedRunFolder.objects.all()
    print(f"Unified folders: {[f.id for f in unified_folders]}")

if __name__ == "__main__":
    check_missing_folders()