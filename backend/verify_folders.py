import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from instagram_data.models import Folder, InstagramPost
from facebook_data.models import Folder as FBFolder, FacebookPost

print('FINAL STATE - PROJECT 6')
print('\nInstagram Folders:')
for f in Folder.objects.filter(project_id=6):
    posts = InstagramPost.objects.filter(folder_id=f.id)
    usernames = posts.values_list('user_posted', flat=True).distinct()
    print(f'  Folder {f.id}: {f.name}')
    print(f'    Unified Job: {f.unified_job_folder_id} ({f.unified_job_folder.name if f.unified_job_folder else "None"})')
    print(f'    Posts: {posts.count()}')
    print(f'    Users: {list(set([u for u in usernames if u]))[:5]}')

print('\nFacebook Folders:')
for f in FBFolder.objects.filter(project_id=6):
    posts = FacebookPost.objects.filter(folder_id=f.id)
    print(f'  Folder {f.id}: {f.name}')
    print(f'    Unified Job: {f.unified_job_folder_id} ({f.unified_job_folder.name if f.unified_job_folder else "None"})')
    print(f'    Posts: {posts.count()}')
