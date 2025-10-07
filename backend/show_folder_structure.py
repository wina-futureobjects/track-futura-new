import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from track_accounts.models import UnifiedRunFolder
from instagram_data.models import Folder as IGFolder
from facebook_data.models import Folder as FBFolder

def print_folder_tree(folder, indent=0):
    """Recursively print folder tree"""
    prefix = "  " * indent
    print(f"{prefix}[{folder.folder_type}] ID:{folder.id} - {folder.name}")

    # Print subfolders
    for subfolder in folder.subfolders.all():
        print_folder_tree(subfolder, indent + 1)

    # If this is a job folder, show linked platform folders
    if folder.folder_type == 'job':
        # Check Instagram folders
        ig_folders = IGFolder.objects.filter(unified_job_folder=folder)
        for ig_folder in ig_folders:
            posts_count = ig_folder.posts.count()
            print(f"{prefix}  [instagram] ID:{ig_folder.id} - {ig_folder.name} ({posts_count} posts)")

        # Check Facebook folders
        fb_folders = FBFolder.objects.filter(unified_job_folder=folder)
        for fb_folder in fb_folders:
            posts_count = fb_folder.posts.count()
            print(f"{prefix}  [facebook] ID:{fb_folder.id} - {fb_folder.name} ({posts_count} posts)")

print("=== UNIFIED FOLDER STRUCTURE ===\n")

# Get all run folders for project 6
run_folders = UnifiedRunFolder.objects.filter(project_id=6, folder_type='run').order_by('-created_at')

for run_folder in run_folders:
    print_folder_tree(run_folder)
    print()
