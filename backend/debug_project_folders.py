#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import Project
from instagram_data.models import Folder as InstagramFolder
from facebook_data.models import Folder as FacebookFolder
from tiktok_data.models import Folder as TikTokFolder
from linkedin_data.models import Folder as LinkedInFolder

def debug_project_associations():
    print("=== PROJECT FOLDER ASSOCIATION DEBUG ===\n")
    
    # Check Projects
    projects = Project.objects.all()
    print(f"Total Projects: {projects.count()}")
    for project in projects:
        print(f"  - Project ID: {project.id}, Name: {project.name}")
    
    print("\n=== INSTAGRAM FOLDERS ===")
    instagram_folders = InstagramFolder.objects.all()
    print(f"Total Instagram Folders: {instagram_folders.count()}")
    orphaned_instagram = InstagramFolder.objects.filter(project_id__isnull=True)
    print(f"Instagram Folders without project: {orphaned_instagram.count()}")
    
    for folder in instagram_folders:
        project_name = folder.project.name if folder.project else "NO PROJECT"
        print(f"  - Folder ID: {folder.id}, Name: {folder.name}, Project: {project_name} (ID: {folder.project_id}), Category: {folder.category}")
    
    print("\n=== FACEBOOK FOLDERS ===")
    facebook_folders = FacebookFolder.objects.all()
    print(f"Total Facebook Folders: {facebook_folders.count()}")
    orphaned_facebook = FacebookFolder.objects.filter(project_id__isnull=True)
    print(f"Facebook Folders without project: {orphaned_facebook.count()}")
    
    for folder in facebook_folders:
        project_name = folder.project.name if folder.project else "NO PROJECT"
        print(f"  - Folder ID: {folder.id}, Name: {folder.name}, Project: {project_name} (ID: {folder.project_id}), Category: {folder.category}")
    
    print("\n=== TIKTOK FOLDERS ===")
    tiktok_folders = TikTokFolder.objects.all()
    print(f"Total TikTok Folders: {tiktok_folders.count()}")
    orphaned_tiktok = TikTokFolder.objects.filter(project_id__isnull=True)
    print(f"TikTok Folders without project: {orphaned_tiktok.count()}")
    
    for folder in tiktok_folders:
        project_name = folder.project.name if folder.project else "NO PROJECT"
        print(f"  - Folder ID: {folder.id}, Name: {folder.name}, Project: {project_name} (ID: {folder.project_id})")
    
    print("\n=== LINKEDIN FOLDERS ===")
    linkedin_folders = LinkedInFolder.objects.all()
    print(f"Total LinkedIn Folders: {linkedin_folders.count()}")
    orphaned_linkedin = LinkedInFolder.objects.filter(project_id__isnull=True)
    print(f"LinkedIn Folders without project: {orphaned_linkedin.count()}")
    
    for folder in linkedin_folders:
        project_name = folder.project.name if folder.project else "NO PROJECT"
        print(f"  - Folder ID: {folder.id}, Name: {folder.name}, Project: {project_name} (ID: {folder.project_id})")
    
    print("\n=== SUMMARY ===")
    total_orphaned = orphaned_instagram.count() + orphaned_facebook.count() + orphaned_tiktok.count() + orphaned_linkedin.count()
    print(f"Total orphaned folders (without project): {total_orphaned}")
    
    if total_orphaned > 0:
        print("\nFOUND ORPHANED FOLDERS! This indicates the project association bug.")
        return False
    else:
        print("All folders have proper project associations.")
        return True

if __name__ == "__main__":
    debug_project_associations() 