import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from track_accounts.models import UnifiedRunFolder
from instagram_data.models import Folder as IGFolder, InstagramPost
from facebook_data.models import Folder as FBFolder, FacebookPost

print("=== ALL INSTAGRAM FOLDERS WITH POSTS ===")
for folder in IGFolder.objects.filter(project_id=6):
    posts_count = InstagramPost.objects.filter(folder=folder).count()
    if posts_count > 0:
        print(f"Folder ID: {folder.id}, Name: {folder.name}")
        print(f"  Posts: {posts_count}")
        print(f"  Linked to Job Folder: {folder.unified_job_folder_id}")
        print()

print("=== ALL FACEBOOK FOLDERS WITH POSTS ===")
for folder in FBFolder.objects.filter(project_id=6):
    posts_count = FacebookPost.objects.filter(folder=folder).count()
    if posts_count > 0:
        print(f"Folder ID: {folder.id}, Name: {folder.name}")
        print(f"  Posts: {posts_count}")
        print(f"  Linked to Job Folder: {folder.unified_job_folder_id}")
        print()

print("=== ALL JOB FOLDERS ===")
for job in UnifiedRunFolder.objects.filter(project_id=6, folder_type='job'):
    print(f"Job Folder ID: {job.id}, Name: {job.name}")

    ig_count = IGFolder.objects.filter(unified_job_folder=job).count()
    fb_count = FBFolder.objects.filter(unified_job_folder=job).count()

    print(f"  Linked IG folders: {ig_count}")
    print(f"  Linked FB folders: {fb_count}")
    print()
