import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from track_accounts.models import UnifiedRunFolder
from instagram_data.models import Folder as IGFolder, InstagramPost
from facebook_data.models import Folder as FBFolder, FacebookPost

print('=== JOB FOLDER 58 (Instagram) ===')
job58 = UnifiedRunFolder.objects.get(id=58)
print(f'Name: {job58.name}')
print(f'Folder Type: {job58.folder_type}')

# Check for linked Instagram folders
ig_folders = IGFolder.objects.filter(unified_job_folder=job58)
print(f'\nLinked Instagram folders: {ig_folders.count()}')
for folder in ig_folders:
    posts_count = InstagramPost.objects.filter(folder=folder).count()
    print(f'  - Folder ID: {folder.id}, Name: {folder.name}, Posts: {posts_count}')

# Check for Instagram folders WITHOUT link
orphaned_ig = IGFolder.objects.filter(project_id=6, unified_job_folder__isnull=True)
print(f'\nOrphaned Instagram folders: {orphaned_ig.count()}')
for folder in orphaned_ig:
    posts_count = InstagramPost.objects.filter(folder=folder).count()
    print(f'  - Folder ID: {folder.id}, Name: {folder.name}, Posts: {posts_count}')

print('\n=== JOB FOLDER 61 (Facebook) ===')
job61 = UnifiedRunFolder.objects.get(id=61)
print(f'Name: {job61.name}')
print(f'Folder Type: {job61.folder_type}')

# Check for linked Facebook folders
fb_folders = FBFolder.objects.filter(unified_job_folder=job61)
print(f'\nLinked Facebook folders: {fb_folders.count()}')
for folder in fb_folders:
    posts_count = FacebookPost.objects.filter(folder=folder).count()
    print(f'  - Folder ID: {folder.id}, Name: {folder.name}, Posts: {posts_count}')

# Check for Facebook folders WITHOUT link
orphaned_fb = FBFolder.objects.filter(project_id=6, unified_job_folder__isnull=True)
print(f'\nOrphaned Facebook folders: {orphaned_fb.count()}')
for folder in orphaned_fb:
    posts_count = FacebookPost.objects.filter(folder=folder).count()
    print(f'  - Folder ID: {folder.id}, Name: {folder.name}, Posts: {posts_count}')
