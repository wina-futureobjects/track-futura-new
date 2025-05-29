#!/usr/bin/env python

import os
import sys
import django

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import Project
from instagram_data.models import Folder as InstagramFolder
from facebook_data.models import Folder as FacebookFolder
from tiktok_data.models import Folder as TikTokFolder  
from linkedin_data.models import Folder as LinkedInFolder

def fix_orphaned_folders():
    """
    Fix folders that don't have a project association by:
    1. Identifying orphaned folders
    2. Assigning them to the first available project
    3. If no projects exist, create a default one
    """
    print("=== FIXING ORPHANED FOLDERS ===\n")
    
    # Get all projects
    projects = Project.objects.all()
    if not projects.exists():
        print("No projects found! Creating a default project...")
        default_project = Project.objects.create(
            name="Default Project",
            description="Automatically created project for orphaned folders"
        )
        print(f"Created default project: {default_project.name} (ID: {default_project.id})")
        target_project = default_project
    else:
        target_project = projects.first()
        print(f"Using existing project: {target_project.name} (ID: {target_project.id})")
    
    fixed_count = 0
    
    # Fix Instagram folders
    orphaned_instagram = InstagramFolder.objects.filter(project_id__isnull=True)
    if orphaned_instagram.exists():
        print(f"\nFixing {orphaned_instagram.count()} orphaned Instagram folders...")
        for folder in orphaned_instagram:
            folder.project = target_project
            folder.save()
            print(f"  - Fixed Instagram folder: {folder.name}")
            fixed_count += 1
    
    # Fix Facebook folders
    orphaned_facebook = FacebookFolder.objects.filter(project_id__isnull=True)
    if orphaned_facebook.exists():
        print(f"\nFixing {orphaned_facebook.count()} orphaned Facebook folders...")
        for folder in orphaned_facebook:
            folder.project = target_project
            folder.save()
            print(f"  - Fixed Facebook folder: {folder.name}")
            fixed_count += 1
    
    # Fix TikTok folders
    orphaned_tiktok = TikTokFolder.objects.filter(project_id__isnull=True)
    if orphaned_tiktok.exists():
        print(f"\nFixing {orphaned_tiktok.count()} orphaned TikTok folders...")
        for folder in orphaned_tiktok:
            folder.project = target_project
            folder.save()
            print(f"  - Fixed TikTok folder: {folder.name}")
            fixed_count += 1
    
    # Fix LinkedIn folders
    orphaned_linkedin = LinkedInFolder.objects.filter(project_id__isnull=True)
    if orphaned_linkedin.exists():
        print(f"\nFixing {orphaned_linkedin.count()} orphaned LinkedIn folders...")
        for folder in orphaned_linkedin:
            folder.project = target_project
            folder.save()
            print(f"  - Fixed LinkedIn folder: {folder.name}")
            fixed_count += 1
    
    print(f"\n=== SUMMARY ===")
    print(f"Total folders fixed: {fixed_count}")
    
    if fixed_count > 0:
        print("All orphaned folders have been assigned to a project!")
        print("The folder project association issue has been resolved.")
    else:
        print("No orphaned folders found. All folders already have proper project associations.")
    
    return fixed_count

if __name__ == "__main__":
    try:
        fixed_count = fix_orphaned_folders()
        if fixed_count > 0:
            print(f"\n✅ Successfully fixed {fixed_count} orphaned folders!")
        else:
            print("\n✅ No fixes needed - all folders properly associated!")
    except Exception as e:
        print(f"\n❌ Error fixing folders: {e}")
        sys.exit(1) 